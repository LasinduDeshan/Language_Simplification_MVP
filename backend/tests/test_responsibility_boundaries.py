import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.database.models import Task, LearnerProfile, ActivitySession, Attempt, TaskResult
from app.personalization.profile_updater import profile_updater

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

def test_vocabulary_task_updates_only_vocabulary_domain(db_session):
    """
    Test 1: Completing a vocabulary task updates ONLY vocabulary_score
    and increments vocabulary_evidence_count while leaving grammar, comprehension,
    and instruction-following scores unchanged.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.category == "vocabulary").first()
    assert learner is not None
    assert task is not None

    if learner.vocabulary_score >= 95.0:
        learner.vocabulary_score = 50.0
        db_session.commit()

    vocab_before = learner.vocabulary_score
    gram_before = learner.grammar_score
    comp_before = learner.comprehension_score
    inst_before = learner.instruction_following_score
    ev_vocab_before = learner.vocabulary_evidence_count or 0
    ev_gram_before = learner.grammar_evidence_count or 0
    screening_risk_before = learner.screening_risk_level or learner.risk_support_level

    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="success",
        attempt_number=1,
        assistance_level="independent",
        adult_confirmed=True
    )

    assert res["target_domain"] == "vocabulary"
    assert res["risk_changed"] is False
    assert learner.vocabulary_score > vocab_before
    assert learner.grammar_score == gram_before
    assert learner.comprehension_score == comp_before
    assert learner.instruction_following_score == inst_before
    assert learner.vocabulary_evidence_count == ev_vocab_before + 1
    assert learner.grammar_evidence_count == ev_gram_before
    assert (learner.screening_risk_level or learner.risk_support_level) == screening_risk_before

def test_grammar_task_updates_only_grammar_domain(db_session):
    """
    Test 2: Completing a grammar task updates ONLY grammar_score
    and increments grammar_evidence_count.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.category == "grammar").first()
    assert learner is not None
    assert task is not None

    if learner.grammar_score >= 95.0:
        learner.grammar_score = 50.0
        db_session.commit()

    vocab_before = learner.vocabulary_score
    gram_before = learner.grammar_score
    ev_gram_before = learner.grammar_evidence_count or 0

    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="success",
        attempt_number=1,
        assistance_level="independent",
        adult_confirmed=True
    )

    assert res["target_domain"] == "grammar"
    assert res["risk_changed"] is False
    assert learner.grammar_score > gram_before
    assert learner.vocabulary_score == vocab_before
    assert learner.grammar_evidence_count == ev_gram_before + 1

def test_screening_risk_remains_read_only(db_session):
    """
    Test 3: Regardless of task outcomes (success or escalation),
    screening_risk_level remains unchanged.
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-001").first()
    task = db_session.query(Task).first()
    assert learner is not None

    original_risk = learner.screening_risk_level or learner.risk_support_level

    # Simulate adult escalation
    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="adult_support_required",
        attempt_number=3,
        assistance_level="adult_guided",
        adult_confirmed=True
    )

    assert res["risk_changed"] is False
    assert (learner.screening_risk_level or learner.risk_support_level) == original_risk

def test_unconfirmed_response_rejected_by_profile_updater(db_session):
    """
    Test 4: An unconfirmed attempt cannot trigger a profile score update.
    """
    learner = db_session.query(LearnerProfile).first()
    task = db_session.query(Task).first()

    with pytest.raises(ValueError, match="Cannot update learner performance score without adult confirmation"):
        profile_updater.update_profile_after_session(
            db=db_session,
            learner=learner,
            task=task,
            session_final_outcome="success",
            attempt_number=1,
            adult_confirmed=False
        )

def test_child_view_excludes_sensitive_screening_and_performance_fields(client, db_session):
    """
    Test 5: The child-view backend response must NEVER expose screening_risk_level,
    performance scores (vocab, grammar, comp, instruction), error codes, adult notes,
    or calculation snapshots to prevent client-side inspection leakage.
    """
    learner = db_session.query(LearnerProfile).first()
    task = db_session.query(Task).first()

    s_res = client.post("/api/activity-sessions", json={
        "learner_id": learner.id,
        "task_id": task.id
    })
    session_id = s_res.json()["id"]

    att_res = client.post(f"/api/activity-sessions/{session_id}/attempts")
    assert att_res.status_code == 200
    child_view = att_res.json()["child_view"]

    # Assert strictly child-safe
    forbidden_keys = [
        "screening_risk_level",
        "risk_level",
        "risk_support_level",
        "vocabulary_score",
        "grammar_score",
        "comprehension_score",
        "instruction_following_score",
        "grammar_observations",
        "vocabulary_observations",
        "adult_notes",
        "calculation_snapshot",
        "model_confidence"
    ]
    for key in forbidden_keys:
        assert key not in child_view, f"Forbidden key '{key}' leaked in child_view payload!"

    assert "presented_instruction" in child_view
    assert "supportive_message" in child_view
    assert "audio_available" in child_view


def test_child_002_risk_immutability_and_fixture_alignment(client, db_session):
    """
    Regression Test: Proves CHILD-002 baseline screening risk is 'moderate' (aligned with Component 1 fixture)
    and that consecutive educational tasks/evaluations cannot alter screening_risk_level.
    """
    import os, json
    
    # 1. Verify fixture alignment
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    fixture_path = os.path.join(base_dir, "data", "integration_fixtures", "component1_inputs", "CHILD-002.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixture_data = json.load(f)
    assert fixture_data["risk_level"] == "moderate"

    # 2. Verify learner in DB has moderate screening risk
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    assert learner is not None
    assert learner.screening_risk_level == "moderate"

    # 3. Simulate multiple activity runs with success and failure
    task = db_session.query(Task).filter(Task.category == "vocabulary").first()
    
    for outcome in ["success", "adult_support_required", "success"]:
        res = profile_updater.update_profile_after_session(
            db=db_session,
            learner=learner,
            task=task,
            session_final_outcome=outcome,
            attempt_number=1,
            adult_confirmed=True
        )
        assert res["risk_changed"] is False
        assert res["after"]["screening_risk_level"] == "moderate"
        assert res["before"]["screening_risk_level"] == "moderate"
        
        # Verify DB persisted entity remains moderate
        db_session.refresh(learner)
        assert learner.screening_risk_level == "moderate"



