import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_vm_happy_path():
    """Test the happy path for VM creation"""
    # Step 1: Send initial request
    response = client.post("/api/chat", json={"message": "Create an S.4 VM named dev-box"})
    assert response.status_code == 200
    data = response.json()
    assert data["requires_confirmation"] == True
    assert data["operation"] == "create_vm"
    
    # Step 2: Send confirmation
    response = client.post("/api/confirm", json={
        "operation": "create_vm",
        "confirmed": True,
        "parameters": {"name": "dev-box", "flavor": "S.4"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_create_vm_cancelled():
    """Test cancellation of VM creation"""
    # Step 1: Send initial request
    response = client.post("/api/chat", json={"message": "Create an S.4 VM named dev-box"})
    
    # Step 2: Cancel the operation
    response = client.post("/api/confirm", json={
        "operation": "create_vm",
        "confirmed": False,
        "parameters": {"name": "dev-box", "flavor": "S.4"}
    })
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_get_usage():
    """Test getting project usage"""
    response = client.post("/api/chat", json={"message": "What's my project usage?"})
    assert response.status_code == 200
    data = response.json()
    assert data["requires_confirmation"] == False
    assert "vCPUs" in data["message"]

def test_invalid_request():
    """Test handling of invalid requests"""
    response = client.post("/api/chat", json={"message": "Do something completely unrelated"})
    assert response.status_code == 200
    data = response.json()
    assert "I'm sorry" in data["message"]
