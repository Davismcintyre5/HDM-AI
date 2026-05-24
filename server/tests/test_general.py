# ====================================================================================================
# server/tests/test_general.py
# ====================================================================================================
"""
HDM AI - General AI Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "HDM AI"
    assert data["status"] == "running"


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register():
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123!",
        },
    )
    assert response.status_code in [200, 400]  # 200 success, 400 already exists


def test_login_fail():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass1!",
        },
    )
    assert response.status_code == 401


def test_general_chat_no_auth():
    """Test chat endpoint without auth."""
    response = client.post(
        "/api/v1/general/chat",
        json={"message": "Hello"},
    )
    assert response.status_code == 401


def test_smartpos_public_chat_no_auth():
    """Test SmartPOS public chat without API key."""
    response = client.post(
        "/api/v1/smartpos/public/chat",
        json={"message": "Hello"},
    )
    assert response.status_code == 401


def test_admin_stats_no_auth():
    """Test admin stats without auth."""
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 401