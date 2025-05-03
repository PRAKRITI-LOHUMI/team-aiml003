from neutronclient.v2_0 import client as neutron_client
from .auth import get_session

def get_neutron_client():
    """Return an authenticated Neutron client"""
    return neutron_client.Client(session=get_session())

def create_network(name):
    """Create a private network with the given name"""
    client = get_neutron_client()
    body = {
        'network': {
            'name': name,
            'admin_state_up': True
        }
    }
    network = client.create_network(body=body)
    
    # Create a subnet for the network
    subnet_body = {
        'subnet': {
            'name': f"{name}-subnet",
            'network_id': network['network']['id'],
            'ip_version': 4,
            'cidr': '192.168.1.0/24'
        }
    }
    subnet = client.create_subnet(subnet_body)
    
    return {
        'network': network['network'],
        'subnet': subnet['subnet']
    }

def delete_network(name):
    """Delete a network by name"""
    client = get_neutron_client()
    networks = client.list_networks(name=name)['networks']
    if not networks:
        raise Exception(f"Network {name} not found")
    network = networks[0]
    
    # Delete all subnets first
    for subnet_id in network['subnets']:
        client.delete_subnet(subnet_id)
    
    # Delete the network
    client.delete_network(network['id'])
    return {"status": "deleted", "name": name}
