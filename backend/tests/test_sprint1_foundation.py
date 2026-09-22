import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.2"

def test_tasks_endpoint(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 10
    task_codes = [t["task_code"] for t in tasks]
    assert "TASK-ENG-001" in task_codes
    assert "TASK-ENG-002" in task_codes

def test_learners_endpoint(client):
    response = client.get("/api/learners")
    assert response.status_code == 200
    learners = response.json()
    assert len(learners) >= 5
    codes = [l["learner_code"] for l in learners]
    assert "CHILD-001" in codes
    assert "CHILD-002" in codes

def test_scenarios_endpoint(client):
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 20

def test_end_to_end_initial_adaptation_and_attempt(client):
    # 1. Fetch learner and task
    learners = client.get("/api/learners").json()
    tasks = client.get("/api/tasks").json()
    learner_id = learners[0]["id"]
    task = next(t for t in tasks if t.get("task_code") == "TASK-ENG-001")
    task_id = task["id"]

    # 2. Create Experiment Run
    exp_res = client.post("/api/experiments", json={
        "learner_id": learner_id,
        "task_id": task_id,
        "generation_mode": "rule"
    })
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    exp_id = exp_data["id"]
    assert exp_data["status"] == "active"

    # 3. Generate Initial Adaptation (BEFORE attempt 1)
    adapt_res = client.post(f"/api/experiments/{exp_id}/initial-adaptation")
    assert adapt_res.status_code == 200
    adapt_data = adapt_res.json()
    assert adapt_data["source_attempt_id"] is None
    assert adapt_data["target_attempt_number"] == 1
    assert len(adapt_data["child_instruction"]) > 0
    adapt_id = adapt_data["id"]

    # 4. Record Attempt 1 with incorrect response -> should trigger next adaptation for Attempt 2
    att1_res = client.post(f"/api/experiments/{exp_id}/attempts", json={
        "adaptation_id": adapt_id,
        "speech_transcript": "Paper on rug.",
        "speech_confidence": 0.88,
        "response_time_ms": 14000,
        "completion_status": "completed"
    })
    assert att1_res.status_code == 200
    att1_data = att1_res.json()
    assert att1_data["attempt"]["attempt_number"] == 1
    assert att1_data["attempt"]["adaptation_id"] == adapt_id
    assert att1_data["attempt"]["concept_result"] == "incorrect"
    assert att1_data["next_adaptation"] is not None
    assert att1_data["next_adaptation"]["target_attempt_number"] == 2
    adapt2_id = att1_data["next_adaptation"]["id"]

    # 5. Record Attempt 2 with correct response -> should complete the experiment
    att2_res = client.post(f"/api/experiments/{exp_id}/attempts", json={
        "adaptation_id": adapt2_id,
        "speech_transcript": "crayons in box, paper in green bin",
        "speech_confidence": 0.95,
        "response_time_ms": 9000,
        "completion_status": "completed"
    })
    assert att2_res.status_code == 200
    att2_data = att2_res.json()
    assert att2_data["attempt"]["attempt_number"] == 2
    assert att2_data["attempt"]["concept_result"] == "correct"
    assert att2_data["experiment_status"] == "completed"
    assert att2_data["final_outcome"] == "success"
    assert att2_data["next_adaptation"] is None

    # 6. Verify History
    hist_res = client.get(f"/api/experiments/{exp_id}/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert len(hist_data["attempts"]) == 2
    assert len(hist_data["adaptations"]) == 2

