import json
import re

class RuleBasedIntentParser:
    def extract_intent(self, user_message):
        """Simple rule-based intent parsing"""
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
