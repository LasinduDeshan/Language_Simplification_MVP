"""Tests for Researcher Quality API endpoints, async 202, auth, and child-role rejection."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_child_access_rejection():
    """Child/learner role is rejected with HTTP 403 Forbidden."""
    response = client.post(
        "/api/v1/datasets/quality/validate",
        json={"dataset_layer": "all"},
        headers={"X-User-Role": "child"}
    )
    assert response.status_code == 403
    assert "restricted from child/learner access" in response.json()["detail"]


def test_async_validation_run_initiation():
    """Researcher triggers async validation run receiving 202 Accepted."""
    response = client.post(
        "/api/v1/datasets/quality/validate",
        json={"dataset_layer": "all", "enable_nlp": True},
        headers={"X-User-Role": "researcher", "X-Idempotency-Key": "test-key-001"}
    )
    assert response.status_code == 202
    data = response.json()
    assert "run_id" in data
    assert data["status"] in ("queued", "running", "completed")


def test_get_runs_and_review_queue():
    """Queries runs and review queue via API."""
    response = client.get(
        "/api/v1/datasets/quality/review-queue",
        headers={"X-User-Role": "researcher"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
