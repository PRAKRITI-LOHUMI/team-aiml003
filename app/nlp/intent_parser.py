from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import torch
import re

class OpenHermesIntentParser:
    def __init__(self):
        # Load the model and tokenizer
        self.model_name = "teknium/OpenHermes-2.5-Mistral-7B"
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Model loaded successfully")
        
    def extract_intent(self, user_message):
        """Extract intent and entities from user message using OpenHermes"""
        messages = [
            {"role": "system", "content": "You extract intents and entities from cloud operations requests."},
            {"role": "user", "content": f"""
            Extract the intent and entities from this cloud operations request: "{user_message}"
            Possible intents: create_vm, resize_vm, delete_vm, create_network, create_volume, delete_volume, get_usage
            Format: {{"intent": "intent_name", "entities": {{"entity1": "value1", "entity2": "value2"}}}}
            """}
        ]
        
        # Format messages using ChatML format
        input_text = self.tokenizer.apply_chat_template(
            messages, 
            add_generation_prompt=True,
            return_tensors="pt"
        ).to(self.model.device)
        
        # Generate response
        outputs = self.model.generate(
            input_text,
            max_new_tokens=256,
            temperature=0.1,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the assistant's response
        assistant_response = response.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', assistant_response, re.DOTALL)
            if json_match:
                return json_match.group(0)
            else:
                return self._fallback_intent_parsing(user_message)
        except:
            # Fallback to simple rule-based parsing if JSON parsing fails
            return self._fallback_intent_parsing(user_message)
    
    def _fallback_intent_parsing(self, user_message):
        """Simple rule-based fallback for intent parsing"""
        intent = "unknown"
        entities = {}
        
        message = user_message.lower()
        
        if "create" in message and "vm" in message:
            intent = "create_vm"
            # Extract name and flavor using simple rules
            if "named" in message:
                name_parts = message.split("named")
                if len(name_parts) > 1:
                    entities["name"] = name_parts[1].strip().split()[0]
            else:
                entities["name"] = "default-vm"
                
            if "s.4" in message:
                entities["flavor"] = "S.4"
            elif "m.8" in message:
                entities["flavor"] = "M.8"
            else:
                entities["flavor"] = "default-flavor"
            
        elif "resize" in message and "vm" in message:
            intent = "resize_vm"
            # Extract VM name
            if "resize" in message:
                parts = message.split("resize")
                if len(parts) > 1:
                    name_parts = parts[1].strip().split()
                    if len(name_parts) > 0:
                        entities["name"] = name_parts[0]
            
            # Extract flavor
            if "to" in message:
                flavor_parts = message.split("to")
                if len(flavor_parts) > 1:
                    flavor = flavor_parts[1].strip().split()[0]
                    entities["flavor"] = flavor
            
            if "flavor" not in entities:
                if "s.4" in message:
                    entities["flavor"] = "S.4"
                elif "m.8" in message:
                    entities["flavor"] = "M.8"
                else:
                    entities["flavor"] = "default-flavor"
            
        elif "delete" in message and "vm" in message:
            intent = "delete_vm"
            if "delete" in message:
                parts = message.split("delete")
                if len(parts) > 1:
                    vm_parts = parts[1].strip().split()
                    if len(vm_parts) > 1 and vm_parts[0].lower() == "the" and vm_parts[1].lower() == "vm":
                        if len(vm_parts) > 2:
                            entities["name"] = vm_parts[2]
                    elif len(vm_parts) > 0:
                        entities["name"] = vm_parts[0]
            
        elif "create" in message and "network" in message:
            intent = "create_network"
            if "called" in message:
                parts = message.split("called")
                if len(parts) > 1:
                    entities["name"] = parts[1].strip().split()[0]
            else:
                entities["name"] = "default-network"
            
        elif "create" in message and "volume" in message:
            intent = "create_volume"
            if "named" in message:
                parts = message.split("named")
                if len(parts) > 1:
                    entities["name"] = parts[1].strip().split()[0]
            else:
                entities["name"] = "default-volume"
            
            # Try to extract size
            size_match = re.search(r'(\d+)\s*gb', message, re.IGNORECASE)
            if size_match:
                entities["size"] = int(size_match.group(1))
            else:
                entities["size"] = 100  # Default size
            
        elif "delete" in message and "volume" in message:
            intent = "delete_volume"
            if "delete" in message:
                parts = message.split("delete")
                if len(parts) > 1:
                    volume_parts = parts[1].strip().split()
                    if len(volume_parts) > 1 and volume_parts[0].lower() == "volume":
                        if len(volume_parts) > 1:
                            entities["name"] = volume_parts[1]
                    elif len(volume_parts) > 0:
                        entities["name"] = volume_parts[0]
            
        elif "usage" in message or "quota" in message or "project usage" in message:
            intent = "get_usage"
        
        return json.dumps({"intent": intent, "entities": entities})
