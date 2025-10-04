"""
Tests for chat endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_token():
    """Get authentication token for tests"""
    client.post("/auth/register", json={
        "email": "chattest@example.com",
        "username": "chattest",
        "password": "testpass123"
    })
    
    response = client.post("/auth/token", data={
        "username": "chattest",
        "password": "testpass123"
    })
    return response.json()["access_token"]


def test_create_chat_session(auth_token):
    """Test creating a chat session"""
    response = client.post(
        "/chat/sessions",
        json={"title": "Test Chat"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["title"] == "Test Chat"


def test_list_chat_sessions(auth_token):
    """Test listing chat sessions"""
    # Create a session first
    client.post(
        "/chat/sessions",
        json={"title": "List Test Chat"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # List sessions
    response = client.get(
        "/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)


def test_chat_query(auth_token):
    """Test sending a chat query"""
    response = client.post(
        "/chat/query",
        json={"query": "Hello, how are you?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "session_id" in data


def test_folder_scoped_query(auth_token):
    """Test query with folder scope"""
    # Create folder
    folder_response = client.post(
        "/folders/",
        json={"name": "Query Test Folder"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    folder_id = folder_response.json()["id"]
    
    # Query with folder scope
    response = client.post(
        "/chat/query",
        json={
            "query": "Test query",
            "folder_id": folder_id
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
