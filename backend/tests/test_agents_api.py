"""
Tests for Agent API - TDD Approach
Tests will fail initially (Red), then implementation will make them pass (Green)
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_all_ideas_for_agents():
    """Test GET /api/agents/ideas - should return list of ideas"""
    response = client.get("/api/agents/ideas")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "ideas" in data
    assert isinstance(data["ideas"], list)


def test_get_idea_for_agents():
    """Test GET /api/agents/ideas/{id} - should return specific idea"""
    # First get all ideas to find a valid ID
    all_ideas = client.get("/api/agents/ideas")
    if all_ideas.status_code == 200 and all_ideas.json()["ideas"]:
        idea_id = all_ideas.json()["ideas"][0]["slug"]
        response = client.get(f"/api/agents/ideas/{idea_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "idea" in data


def test_enrich_idea():
    """Test PUT /api/agents/ideas/{id}/enrich - should enrich idea"""
    # Get a valid idea ID first
    all_ideas = client.get("/api/agents/ideas")
    if all_ideas.status_code == 200 and all_ideas.json()["ideas"]:
        idea_id = all_ideas.json()["ideas"][0]["slug"]
        
        enrichment_data = {
            "products": [
                {
                    "title": "Test Product",
                    "description": "Test Description",
                    "target_audience": "Test Audience",
                    "revenue_model": "subscription"
                }
            ],
            "research": {
                "market_analysis": "Test market analysis"
            },
            "agent_notes": "Test notes",
            "status": "researched"
        }
        
        response = client.put(f"/api/agents/ideas/{idea_id}/enrich", json=enrichment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


def test_get_agent_tasks():
    """Test GET /api/agents/tasks - should return tasks list"""
    response = client.get("/api/agents/tasks")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "tasks" in data


def test_create_agent_task():
    """Test POST /api/agents/tasks - should create task"""
    task_data = {
        "id": "test_task_1",
        "idea_id": "test_idea_1",
        "task_type": "research",
        "priority": "medium",
        "status": "pending",
        "created_at": "2025-01-01T00:00:00"
    }
    
    response = client.post("/api/agents/tasks", json=task_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_get_agent_stats():
    """Test GET /api/agents/stats - should return statistics"""
    response = client.get("/api/agents/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "stats" in data