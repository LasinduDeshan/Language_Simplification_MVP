import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.database.models import Task, LearnerProfile
from app.response_analysis.answer_checker import answer_checker

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

def test_concept_vs_target_skill_preposition(db_session):
    """
    If the activity tests preposition use (GRAM-PREP-001):
    - 'Fish live water.' -> Concept: correct, Target skill: incorrect, Retry: required
    - 'The fish lives in water.' -> Concept: correct, Target skill: correct, Retry: not required
    """
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()
    assert task is not None

    # Case 1: Missing preposition
    res1 = answer_checker.evaluate_answer(task, transcript="Fish live water.")
    assert res1["concept_result"] == "correct"
    assert res1["target_skill_result"] == "incorrect"
    assert "missing_preposition" in res1["grammar_observations"]
    assert res1["retry_required"] is True
    assert res1["retry_reason"] == "target_skill_not_demonstrated"

    # Case 2: Correct preposition
    res2 = answer_checker.evaluate_answer(task, transcript="The fish lives in water.")
    assert res2["concept_result"] == "correct"
    assert res2["target_skill_result"] == "correct"
    assert res2["retry_required"] is False

def test_concept_vs_target_skill_category(db_session):
    """
    If the activity tests categorization (VOC-CAT-001):
    - Child selects or says 'apple' -> Concept: correct, Target skill: correct
    - Child says 'tiger' -> Concept: incorrect, Target skill: incorrect
    """
    task = db_session.query(Task).filter(Task.task_code == "VOC-CAT-001").first()
    assert task is not None

    res1 = answer_checker.evaluate_answer(task, transcript="apple")
    assert res1["concept_result"] == "correct"
    assert res1["target_skill_result"] == "correct"
    assert res1["retry_required"] is False

    res2 = answer_checker.evaluate_answer(task, transcript="tiger")
    assert res2["concept_result"] == "incorrect"
    assert res2["target_skill_result"] == "incorrect"
    assert res2["retry_required"] is True

def test_completion_statuses_handling(db_session):
    """
    Completion statuses 'no_response', 'asked_for_help', 'skipped'
    must produce retry_required without throwing errors.
    """
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()
    assert task is not None

    for status in ["no_response", "asked_for_help", "skipped"]:
        res = answer_checker.evaluate_answer(task, transcript="", completion_status=status)
        assert res["concept_result"] == "unclear"
        assert res["target_skill_result"] == "incorrect"
        assert res["retry_required"] is True
        assert res["retry_reason"] == f"child_{status}"

def test_strict_confirmation_before_analysis(client, db_session):
    """
    Attempting to analyse an unconfirmed attempt must raise HTTP 400.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()

    # 1. Create Session
    s_res = client.post("/api/activity-sessions", json={
        "learner_id": learner.id,
        "task_id": task.id
    })
    assert s_res.status_code == 200
    session_id = s_res.json()["id"]

    # 2. Create Attempt (Generates instruction before child sees it)
    att_res = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att_res.status_code == 200
    attempt_id = att_res.json()["attempt"]["id"]

    # 3. Record Response
    rec_res = client.patch(f"/api/attempts/{attempt_id}/response", json={
        "response_source": "adult_transcribed",
        "manual_transcript": "Fish live water.",
        "response_time_ms": 12000,
        "completion_status": "completed"
    })
    assert rec_res.status_code == 200
    assert rec_res.json()["adult_confirmed"] is False

    # 4. Attempt Analysis BEFORE Confirmation -> MUST FAIL
    anal_fail = client.post(f"/api/attempts/{attempt_id}/analyse")
    assert anal_fail.status_code == 400
    assert "confirmation" in anal_fail.json()["detail"].lower()

    # 5. Confirm Response
    conf_res = client.post(f"/api/attempts/{attempt_id}/confirm-response", json={
        "confirmed": True
    })
    assert conf_res.status_code == 200
    assert conf_res.json()["adult_confirmed"] is True

    # 6. Analyse Confirmed Response -> SUCCEEDS
    anal_ok = client.post(f"/api/attempts/{attempt_id}/analyse")
    assert anal_ok.status_code == 200
    data = anal_ok.json()
    assert data["concept_result"] == "correct"
    assert data["target_skill_result"] == "incorrect"
    assert "missing_preposition" in data["grammar_observations"]

def test_adult_review_preserves_automatic_and_final_results(client, db_session):
    """
    Adult review overrides must update final_concept_result while keeping
    automatic_analysis_snapshot intact.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.task_code == "GRAM-PREP-001").first()

    # Create session, attempt, record, confirm, analyse
    s_id = client.post("/api/activity-sessions", json={"learner_id": learner.id, "task_id": task.id}).json()["id"]
    att_id = client.post(f"/api/activity-sessions/{s_id}/attempts").json()["attempt"]["id"]
    client.patch(f"/api/attempts/{att_id}/response", json={"manual_transcript": "Fish live water."})
    client.post(f"/api/attempts/{att_id}/confirm-response", json={"confirmed": True})
    client.post(f"/api/attempts/{att_id}/analyse")

    # Review & Override
    rev_res = client.patch(f"/api/attempts/{att_id}/review", json={
        "final_concept_result": "correct",
        "final_target_skill_result": "correct",
        "final_retry_required": False,
        "override_reason": "Educator observed child pointing directly to the water tank.",
        "reviewed_by_user_id": "RESEARCHER-01",
        "adult_notes": "Accepted non-verbal gesture as valid prepositional meaning."
    })
    assert rev_res.status_code == 200
    att_data = rev_res.json()
    assert att_data["final_concept_result"] == "correct"
    assert att_data["final_target_skill_result"] == "correct"
    assert att_data["final_retry_required"] is False
    assert att_data["automatic_analysis_snapshot"]["target_skill_result"] == "incorrect"
    assert att_data["reviewed_by_user_id"] == "RESEARCHER-01"
