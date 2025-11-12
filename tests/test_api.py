"""Pytest tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient

from backend import database
from backend.main import app

# Initialize test database
TEST_DB = "test_moderation.db"


@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Set up test database before each test."""
    monkeypatch.setattr(database, "DATABASE_PATH", TEST_DB)
    database.init_db()
    yield
    # Cleanup: delete test database
    import os
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_create_flag(client):
    """Test creating a flagged item."""
    response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "This is a test message"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content_type"] == "message"
    assert data["content"] == "This is a test message"
    assert data["status"] == "pending"
    assert "priority" in data
    assert "ai_summary" in data
    assert "id" in data


def test_create_flag_high_priority(client):
    """Test that violence keyword triggers high priority."""
    response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "This contains violence and threats"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "high"


def test_create_flag_medium_priority(client):
    """Test that spam keyword triggers medium priority."""
    response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "This is spam content"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == "medium"


def test_get_flags(client):
    """Test getting all flags."""
    # Create a flag first
    client.post(
        "/api/flags",
        json={"content_type": "message", "content": "Test message"}
    )
    
    response = client.get("/api/flags")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_flag_by_id(client):
    """Test getting a single flag by ID."""
    # Create a flag first
    create_response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "Test message"}
    )
    flag_id = create_response.json()["id"]
    
    response = client.get(f"/api/flags/{flag_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == flag_id
    assert data["content"] == "Test message"


def test_get_flag_not_found(client):
    """Test getting a non-existent flag."""
    response = client.get("/api/flags/999")
    assert response.status_code == 404


def test_update_flag_status(client):
    """Test updating flag status."""
    # Create a flag first
    create_response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "Test message"}
    )
    flag_id = create_response.json()["id"]
    
    # Update status
    response = client.patch(
        f"/api/flags/{flag_id}",
        json={"status": "approved"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_update_flag_not_found(client):
    """Test updating a non-existent flag."""
    response = client.patch(
        "/api/flags/999",
        json={"status": "approved"}
    )
    assert response.status_code == 404


def test_delete_flag(client):
    """Test deleting a flag."""
    # Create a flag first
    create_response = client.post(
        "/api/flags",
        json={"content_type": "message", "content": "Test message"}
    )
    flag_id = create_response.json()["id"]
    
    # Delete flag
    response = client.delete(f"/api/flags/{flag_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/flags/{flag_id}")
    assert get_response.status_code == 404


def test_delete_flag_not_found(client):
    """Test deleting a non-existent flag."""
    response = client.delete("/api/flags/999")
    assert response.status_code == 404


def test_get_stats(client):
    """Test getting statistics."""
    # Create some flags
    client.post(
        "/api/flags",
        json={"content_type": "message", "content": "violence threat"}
    )
    client.post(
        "/api/flags",
        json={"content_type": "message", "content": "spam content"}
    )
    
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_flags"] == 2
    assert data["high_priority"] == 1
    assert data["medium_priority"] == 1
    assert data["low_priority"] == 0
    assert data["pending_status"] == 2

