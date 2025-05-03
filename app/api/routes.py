from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.openstack import nova, neutron, cinder
import json
from app.nlp.intent_parser import OpenHermesIntentParser
# lightweight alternative
from app.nlp.rule_based_parser import RuleBasedIntentParser
from app.models.database import SessionLocal
from app.models.models import UserInteraction

router = APIRouter(prefix="/api", tags=["openstack"])

# Initialize the OpenHermes intent parser
# intent_parser = OpenHermesIntentParser()

# lightweight alternative
intent_parser = RuleBasedIntentParser()

class VMCreateRequest(BaseModel):
    name: str
    flavor: str

class VolumeCreateRequest(BaseModel):
    name: str
    size: int

class UserRequest(BaseModel):
    message: str

class ConfirmationRequest(BaseModel):
    operation: str
    confirmed: bool
    parameters: dict

@router.post("/vm/create")
async def create_vm(request: VMCreateRequest):
    try:
        instance = nova.create_vm(request.name, request.flavor)
        return {
            "status": "creating", 
            "id": instance.id, 
            "name": request.name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/vm/resize")
async def resize_vm(name: str, flavor: str):
    try:
        server = nova.resize_vm(name, flavor)
        return {
            "status": "resizing",
            "id": server.id,
            "name": name
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/vm/delete")
async def delete_vm(name: str):
    try:
        result = nova.delete_vm(name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/network/create")
async def create_network(name: str):
    try:
        network = neutron.create_network(name)
        return network
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/volume/create")
async def create_volume(request: VolumeCreateRequest):
    try:
        volume = cinder.create_volume(request.name, request.size)
        return {
            "status": "creating",
            "id": volume.id,
            "name": request.name,
            "size": request.size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/volume/delete")
async def delete_volume(name: str):
    try:
        result = cinder.delete_volume(name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/usage")
async def get_usage():
    try:
        nova_client = nova.get_nova_client()
        cinder_client = cinder.get_cinder_client()
        
        servers = nova_client.servers.list()
        volumes = cinder_client.volumes.list()
        
        total_vcpus = sum(nova_client.flavors.get(s.flavor['id']).vcpus for s in servers)
        total_ram = sum(nova_client.flavors.get(s.flavor['id']).ram for s in servers)
        total_volume_gb = sum(v.size for v in volumes)
        
        return {
            "vcpus_used": total_vcpus,
            "ram_mb_used": total_ram,
            "volumes_gb": total_volume_gb,
            "vm_count": len(servers),
            "volume_count": len(volumes)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat")
async def chat(request: UserRequest):
    """Main conversation endpoint"""
    try:
        # Extract intent and entities using OpenHermes
        intent_data = intent_parser.extract_intent(request.message)
        
        # Parse the JSON response
        try:
            intent_dict = json.loads(intent_data)
        except json.JSONDecodeError:
            # If the model didn't return valid JSON, try to extract it
            # This handles cases where the model might add explanatory text
            import re
            json_match = re.search(r'\{.*\}', intent_data, re.DOTALL)
            if json_match:
                try:
                    intent_dict = json.loads(json_match.group(0))
                except:
                    intent_dict = {"intent": "unknown", "entities": {}}
            else:
                intent_dict = {"intent": "unknown", "entities": {}}
        
        intent = intent_dict.get("intent")
        entities = intent_dict.get("entities", {})
        
        # Log the incoming request
        db = SessionLocal()
        interaction = UserInteraction(
            user_message=request.message,
            detected_intent=intent,
            entities=entities,
            system_response=None
        )
        db.add(interaction)
        db.commit()
        
        # Handle different intents
        if intent == "create_vm":
            vm_name = entities.get("name")
            flavor = entities.get("flavor")
            
            # Generate confirmation message
            confirmation = f"I'll create a VM named '{vm_name}' with flavor '{flavor}'. Would you like to proceed?"
            
            # Update the response
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "create_vm",
                "parameters": {"name": vm_name, "flavor": flavor}
            }
        
        elif intent == "resize_vm":
            vm_name = entities.get("name")
            flavor = entities.get("flavor")
            
            confirmation = f"I'll resize VM '{vm_name}' to flavor '{flavor}'. Would you like to proceed?"
            
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "resize_vm",
                "parameters": {"name": vm_name, "flavor": flavor}
            }
        
        elif intent == "delete_vm":
            vm_name = entities.get("name")
            
            confirmation = f"I'll delete VM '{vm_name}'. This action cannot be undone. Would you like to proceed?"
            
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "delete_vm",
                "parameters": {"name": vm_name}
            }
        
        elif intent == "create_network":
            network_name = entities.get("name")
            
            confirmation = f"I'll create a private network named '{network_name}'. Would you like to proceed?"
            
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "create_network",
                "parameters": {"name": network_name}
            }
        
        elif intent == "create_volume":
            volume_name = entities.get("name")
            size = entities.get("size")
            
            confirmation = f"I'll create a {size} GB volume named '{volume_name}'. Would you like to proceed?"
            
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "create_volume",
                "parameters": {"name": volume_name, "size": size}
            }
        
        elif intent == "delete_volume":
            volume_name = entities.get("name")
            
            confirmation = f"I'll delete volume '{volume_name}'. This action cannot be undone. Would you like to proceed?"
            
            interaction.system_response = confirmation
            db.commit()
            db.close()
            
            return {
                "message": confirmation,
                "requires_confirmation": True,
                "operation": "delete_volume",
                "parameters": {"name": volume_name}
            }
        
        elif intent == "get_usage":
            # No confirmation needed for read-only operations
            usage = await get_usage()
            
            response = f"Current project usage:\n- vCPUs: {usage['vcpus_used']}\n- RAM: {usage['ram_mb_used']} MB\n- Storage: {usage['volumes_gb']} GB\n- VMs: {usage['vm_count']}\n- Volumes: {usage['volume_count']}"
            
            interaction.system_response = response
            interaction.operation_executed = "get_usage"
            interaction.operation_result = usage
            db.commit()
            db.close()
            
            return {
                "message": response,
                "requires_confirmation": False
            }
        
        else:
            response = "I'm sorry, I couldn't understand that request. Please try again with a different phrasing."
            
            interaction.system_response = response
            db.commit()
            db.close()
            
            return {
                "message": response,
                "requires_confirmation": False
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm")
async def confirm_operation(request: ConfirmationRequest):
    """Handle user confirmation for operations"""
    try:
        db = SessionLocal()
        
        if not request.confirmed:
            response = {"status": "cancelled", "message": "Operation cancelled by user"}
            
            # Log the cancellation
            interaction = UserInteraction(
                user_message="User cancelled operation",
                detected_intent=request.operation,
                entities=request.parameters,
                system_response="Operation cancelled",
                operation_executed=None,
                operation_result=None
            )
            db.add(interaction)
            db.commit()
            db.close()
            
            return response
        
        # Execute the confirmed operation based on the operation type
        if request.operation == "create_vm":
            result = await create_vm(VMCreateRequest(name=request.parameters.get("name"), flavor=request.parameters.get("flavor")))
            response = {"status": "success", "message": f"VM {request.parameters.get('name')} is being created", "details": result}
        
        elif request.operation == "resize_vm":
            result = await resize_vm(request.parameters.get("name"), request.parameters.get("flavor"))
            response = {"status": "success", "message": f"VM {request.parameters.get('name')} is being resized to {request.parameters.get('flavor')}", "details": result}
        
        elif request.operation == "delete_vm":
            result = await delete_vm(request.parameters.get("name"))
            response = {"status": "success", "message": f"VM {request.parameters.get('name')} has been deleted", "details": result}
        
        elif request.operation == "create_network":
            result = await create_network(request.parameters.get("name"))
            response = {"status": "success", "message": f"Network {request.parameters.get('name')} has been created", "details": result}
        
        elif request.operation == "create_volume":
            result = await create_volume(VolumeCreateRequest(name=request.parameters.get("name"), size=request.parameters.get("size")))
            response = {"status": "success", "message": f"Volume {request.parameters.get('name')} is being created", "details": result}
        
        elif request.operation == "delete_volume":
            result = await delete_volume(request.parameters.get("name"))
            response = {"status": "success", "message": f"Volume {request.parameters.get('name')} has been deleted", "details": result}
        
        else:
            response = {"status": "error", "message": f"Unknown operation: {request.operation}"}
        
        # Log the execution
        interaction = UserInteraction(
            user_message="User confirmed operation",
            detected_intent=request.operation,
            entities=request.parameters,
            system_response=response["message"],
            operation_executed=request.operation,
            operation_result=response
        )
        db.add(interaction)
        db.commit()
        db.close()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
