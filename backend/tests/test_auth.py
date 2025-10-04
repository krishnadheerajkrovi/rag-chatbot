"""
Tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    })
    assert response.status_code in [200, 400]  # 400 if user exists


def test_login_success():
    """Test successful login"""
    # First register
    client.post("/auth/register", json={
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "testpass123"
    })
    
    # Then login
    response = client.post("/auth/token", data={
        "username": "testuser2",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/auth/token", data={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/folders/")
    assert response.status_code == 401
