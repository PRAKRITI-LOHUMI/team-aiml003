from novaclient import client as nova_client
from .auth import get_session

def get_nova_client():
    """Return an authenticated Nova client"""
    return nova_client.Client(2, session=get_session())

def create_vm(name, flavor_name):
    """Create a VM with the specified name and flavor"""
    client = get_nova_client()
    flavor = client.flavors.find(name=flavor_name)
    
    # Get the first available image (update this logic as needed)
    images = list(client.images.list())
    if not images:
        raise Exception("No images available")
    image = images[0]
    
    instance = client.servers.create(name=name, flavor=flavor.id, image=image.id)
    return instance

def resize_vm(vm_name, new_flavor):
    """Resize a VM to a new flavor"""
    client = get_nova_client()
    server = client.servers.find(name=vm_name)
    flavor = client.flavors.find(name=new_flavor)
    server.resize(flavor.id)
    return server

def delete_vm(vm_name):
    """Delete a VM by name"""
    client = get_nova_client()
    server = client.servers.find(name=vm_name)
    server.delete()
    return {"status": "deleted", "name": vm_name}

def get_vm_details(vm_name):
    """Get details of a VM by name"""
    client = get_nova_client()
    server = client.servers.find(name=vm_name)
    return server
