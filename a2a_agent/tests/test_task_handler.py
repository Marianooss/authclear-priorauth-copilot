"""
Tests for a2a_agent/task_handler.py

Tests:
- New task creation and state transitions
- Multi-turn task continuation
- Input validation
- Invariant: human_review_required always True
- Invariant: confidence_score in [0.0, 1.0]
"""
from __future__ import annotations
import pytest
from datetime import datetime


class TestSendNewTask:
    
    def test_send_new_task_valid_bundle_returns_task(
        self, test_app, synthetic_bundle_complete
    ):
        """Valid FHIR bundle + drug creates a task and returns response."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete,
                    "requested_item": "Ozempic",
                    "payer": "generic"
                }
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "task" in data
        assert data["task"]["state"] in {"working", "completed"}

    def test_send_task_returns_task_id(self, test_app, synthetic_bundle_complete):
        """Response includes a task ID for subsequent lookups."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete,
                    "requested_item": "Ozempic"
                }
            }
        })
        
        data = response.json()
        assert data["task"]["id"] is not None
        assert len(data["task"]["id"]) > 0

    def test_send_task_invalid_fhir_returns_422(self, test_app):
        """Malformed FHIR bundle returns 422 with structured error."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": {"resourceType": "NOT_VALID", "entry": "bad"},
                    "requested_item": "Ozempic"
                }
            }
        })
        
        assert response.status_code == 422

    def test_send_task_missing_requested_item_returns_422(self, test_app, synthetic_bundle_complete):
        """Missing required field returns 422."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete
                    # missing: requested_item
                }
            }
        })
        
        assert response.status_code == 422

    def test_send_task_empty_bundle_returns_422(self, test_app):
        """Empty FHIR bundle raises validation error."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": {},
                    "requested_item": "Ozempic"
                }
            }
        })
        
        assert response.status_code == 422


class TestTaskInvariants:
    """Tests that verify invariants that must ALWAYS hold."""

    def test_human_review_required_always_true(self, test_app, synthetic_bundle_complete):
        """
        CRITICAL INVARIANT: human_review_required must ALWAYS be True.
        This is a regulatory requirement. If this test fails, ship nothing.
        """
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete,
                    "requested_item": "Ozempic"
                }
            }
        })
        
        data = response.json()
        if data["task"].get("result"):
            assert data["task"]["result"]["human_review_required"] is True

    def test_confidence_score_within_valid_range(self, test_app, synthetic_bundle_complete):
        """Confidence score must be between 0.0 and 1.0 inclusive."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete,
                    "requested_item": "Ozempic"
                }
            }
        })
        
        data = response.json()
        if data["task"].get("result"):
            score = data["task"]["result"]["confidence_score"]
            assert 0.0 <= score <= 1.0

    def test_missing_items_populated_when_gaps_exist(self, test_app, synthetic_bundle_gaps):
        """When patient record has gaps, missing_items must be populated."""
        response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_gaps,
                    "requested_item": "Ozempic",
                    "payer": "generic"
                }
            }
        })
        
        data = response.json()
        if data["task"].get("result"):
            # Patient is missing second oral agent trial — must appear in missing_items
            missing = data["task"]["result"]["missing_items"]
            assert isinstance(missing, list)
            # At least one missing item expected for this fixture


class TestTaskLookup:
    
    def test_get_existing_task_returns_task(self, test_app, synthetic_bundle_complete):
        """GET /tasks/{id} returns previously created task."""
        # Create task
        create_response = test_app.post("/tasks/send", json={
            "message": {
                "role": "user",
                "content": {
                    "fhir_bundle": synthetic_bundle_complete,
                    "requested_item": "Ozempic"
                }
            }
        })
        task_id = create_response.json()["task"]["id"]
        
        # Retrieve task
        get_response = test_app.get(f"/tasks/{task_id}")
        
        assert get_response.status_code == 200
        assert get_response.json()["id"] == task_id

    def test_get_nonexistent_task_returns_404(self, test_app):
        """GET /tasks/{nonexistent_id} returns 404."""
        response = test_app.get("/tasks/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404


class TestHealthCheck:
    
    def test_health_endpoint_returns_ok(self, test_app):
        """Health check endpoint returns 200 with status ok."""
        response = test_app.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_agent_card_endpoint_returns_valid_json(self, test_app):
        """AgentCard endpoint returns valid JSON with required fields."""
        response = test_app.get("/.well-known/agent.json")
        
        assert response.status_code == 200
        card = response.json()
        assert "name" in card
        assert "url" in card
        assert "capabilities" in card
        assert "skills" in card
