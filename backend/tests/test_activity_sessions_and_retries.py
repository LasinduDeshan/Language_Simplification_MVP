import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.database.models import Task, LearnerProfile, ActivitySession, Attempt

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_high_risk_learner_scaffolding_progression(client, db_session):
    """
    CHILD-001 is high risk with scores < 40:
    - Attempt 1: Must start with Strong support (child-friendly strong)
    - Attempt 2: Strong support + visual/example cue
    - Attempt 3: Strong support + adult modelling
    - Never regresses to mild support.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-001").first()
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()
    assert learner is not None
    assert task is not None

    # 1. Create Session
    s_res = client.post("/api/activity-sessions", json={
        "learner_id": learner.id,
        "task_id": task.id
    })
    assert s_res.status_code == 200
    s_data = s_res.json()
    assert s_data["initial_support_level"] == "strong"
    assert "risk_level_high" in s_data["support_decision_reasons"]
    session_id = s_data["id"]

    # Attempt 1
    att1_res = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att1_res.status_code == 200
    att1 = att1_res.json()["attempt"]
    assert att1["support_level"] == "strong"
    assert att1["adaptation_strategy"] == "strong_child_friendly"
    assert att1["presented_instruction"] == "Choose: in, on, or under."

    # Record & Confirm unsuccessful response for Attempt 1
    client.patch(f"/api/attempts/{att1['id']}/response", json={"manual_transcript": "Fish live water."})
    client.post(f"/api/attempts/{att1['id']}/confirm-response", json={"confirmed": True})
    client.post(f"/api/attempts/{att1['id']}/analyse")
    client.post(f"/api/attempts/{att1['id']}/transition")

    # Attempt 2
    att2_res = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att2_res.status_code == 200
    att2 = att2_res.json()["attempt"]
    assert att2["support_level"] == "strong"
    assert att2["adaptation_strategy"] == "strong_visual_cue"
    assert att2["assistance_level"] == "prompted"

    # Record & Confirm unsuccessful response for Attempt 2
    client.patch(f"/api/attempts/{att2['id']}/response", json={"manual_transcript": "under"})
    client.post(f"/api/attempts/{att2['id']}/confirm-response", json={"confirmed": True})
    client.post(f"/api/attempts/{att2['id']}/analyse")
    client.post(f"/api/attempts/{att2['id']}/transition")

    # Attempt 3
    att3_res = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att3_res.status_code == 200
    att3 = att3_res.json()["attempt"]
    assert att3["support_level"] == "strong"
    assert att3["adaptation_strategy"] == "strong_adult_modelling"
    assert att3["assistance_level"] == "modelled"

    # Attempt 4 must be rejected
    att4_fail = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att4_fail.status_code == 400
    assert "maximum 3 attempts" in att4_fail.json()["detail"].lower()

def test_low_risk_learner_scaffolding_progression(client, db_session):
    """
    CHILD-003 is low risk with scores > 70:
    - Attempt 1: Starts with Mild support
    - Attempt 2: Moderate support
    - Attempt 3: Strong support
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-003").first()
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()

    s_res = client.post("/api/activity-sessions", json={"learner_id": learner.id, "task_id": task.id})
    s_id = s_res.json()["id"]
    assert s_res.json()["initial_support_level"] == "mild"

    att1 = client.post(f"/api/activity-sessions/{s_id}/attempts").json()["attempt"]
    assert att1["support_level"] == "mild"

    client.patch(f"/api/attempts/{att1['id']}/response", json={"manual_transcript": "Fish live water."})
    client.post(f"/api/attempts/{att1['id']}/confirm-response", json={"confirmed": True})
    client.post(f"/api/attempts/{att1['id']}/analyse")
    client.post(f"/api/attempts/{att1['id']}/transition")

    att2 = client.post(f"/api/activity-sessions/{s_id}/attempts").json()["attempt"]
    assert att2["support_level"] == "moderate"

    client.patch(f"/api/attempts/{att2['id']}/response", json={"manual_transcript": "tree"})
    client.post(f"/api/attempts/{att2['id']}/confirm-response", json={"confirmed": True})
    client.post(f"/api/attempts/{att2['id']}/analyse")
    client.post(f"/api/attempts/{att2['id']}/transition")

    att3 = client.post(f"/api/activity-sessions/{s_id}/attempts").json()["attempt"]
    assert att3["support_level"] == "strong"

def test_immutable_learner_profile_snapshot(client, db_session):
    """
    Modifying learner profile metrics after session creation must not alter
    the frozen learner_profile_snapshot stored in ActivitySession.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.task_code == "VOC-NAMING-001").first()
    orig_vocab = learner.vocabulary_score

    s_res = client.post("/api/activity-sessions", json={"learner_id": learner.id, "task_id": task.id})
    s_id = s_res.json()["id"]
    snapshot = s_res.json()["learner_profile_snapshot"]
    assert snapshot["vocabulary_score"] == orig_vocab

    # Mutate learner profile
    learner.vocabulary_score = 99.0
    db_session.commit()

    # Re-fetch session
    s_after = client.get(f"/api/activity-sessions/{s_id}").json()
    assert s_after["learner_profile_snapshot"]["vocabulary_score"] == orig_vocab

    # Reset
    learner.vocabulary_score = orig_vocab
    db_session.commit()

def test_child_view_endpoint_safety(client, db_session):
    """
    GET /api/activity-sessions/{id}/child-view must return pure child-friendly content
    without diagnostic codes, clinical scores, or researcher notes.
    """
    learner = db_session.query(LearnerProfile).first()
    task = db_session.query(Task).filter(Task.task_code == "VOC-NAMING-001").first()

    s_id = client.post("/api/activity-sessions", json={"learner_id": learner.id, "task_id": task.id}).json()["id"]
    client.post(f"/api/activity-sessions/{s_id}/attempts")

    cv_res = client.get(f"/api/activity-sessions/{s_id}/child-view")
    assert cv_res.status_code == 200
    cv = cv_res.json()

    assert "presented_instruction" in cv
    assert "audio_available" in cv
    assert cv["audio_available"] is True

    # Confirm exclusion of researcher/diagnostic fields
    assert "risk_support_level" not in cv
    assert "vocabulary_score" not in cv
    assert "grammar_score" not in cv
    assert "observations" not in cv
    assert "diagnostic_summary" not in cv
