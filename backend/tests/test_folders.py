"""
Tests for folder management endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Get authentication token for tests"""
    # Register and login
    client.post("/auth/register", json={
        "email": "foldertest@example.com",
        "username": "foldertest",
        "password": "testpass123"
    })
    
    response = client.post("/auth/token", data={
        "username": "foldertest",
        "password": "testpass123"
    })
    return response.json()["access_token"]


def test_create_folder(auth_token):
    """Test folder creation"""
    response = client.post(
        "/folders/",
        json={"name": "Test Folder", "description": "Test Description"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Folder"
    assert "id" in data


def test_list_folders(auth_token):
    """Test listing folders"""
    # Create a folder first
    client.post(
        "/folders/",
        json={"name": "List Test Folder"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # List folders
    response = client.get(
        "/folders/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    folders = response.json()
    assert isinstance(folders, list)
    assert len(folders) > 0


def test_archive_folder(auth_token):
    """Test archiving a folder"""
    # Create folder
    create_response = client.post(
        "/folders/",
        json={"name": "Archive Test"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    folder_id = create_response.json()["id"]
    
    # Archive it
    response = client.post(
        f"/folders/{folder_id}/archive",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    
    # Verify it's not in default list
    list_response = client.get(
        "/folders/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    folder_names = [f["name"] for f in list_response.json()]
    assert "Archive Test" not in folder_names


def test_unarchive_folder(auth_token):
    """Test unarchiving a folder"""
    # Create and archive folder
    create_response = client.post(
        "/folders/",
        json={"name": "Unarchive Test"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    folder_id = create_response.json()["id"]
    
    client.post(
        f"/folders/{folder_id}/archive",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Unarchive it
    response = client.post(
        f"/folders/{folder_id}/unarchive",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
