from cinderclient import client as cinder_client
from .auth import get_session

def get_cinder_client():
    """Return an authenticated Cinder client"""
    return cinder_client.Client(3, session=get_session())

def create_volume(name, size):
    """Create a volume with the given name and size in GB"""
    client = get_cinder_client()
    volume = client.volumes.create(size=size, name=name)
    return volume

def delete_volume(name):
    """Delete a volume by name"""
    client = get_cinder_client()
    volume = client.volumes.find(name=name)
    client.volumes.delete(volume)
    return {"status": "deleted", "name": name}

def get_volume_details(name):
    """Get details of a volume by name"""
    client = get_cinder_client()
    volume = client.volumes.find(name=name)
    return volume
