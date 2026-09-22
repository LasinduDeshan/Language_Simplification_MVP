import pytest
from app.database.db import SessionLocal
from app.database.models import LearnerProfile, Task, ActivitySession, Attempt
from app.personalization.profile_updater import profile_updater

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_profile_updater_escalation_penalty(db_session):
    """
    Tests educational profile update when a learner struggles and escalates to adult support:
    - Base delta: -2.5
    - Medium difficulty: x1.2 = -3.0
    - Grammar task: 100% attributed to primary grammar domain (-3.0), vocabulary delta = 0.0
    - Screening risk remains unchanged from Component 1
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.category == "grammar", Task.base_difficulty == "medium").first()
    assert learner is not None
    assert task is not None

    initial_vocab = learner.vocabulary_score
    initial_gram = learner.grammar_score
    screening_risk_before = learner.screening_risk_level or learner.risk_support_level

    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="adult_support_required",
        attempt_number=3,
        grammar_errors_count=0,
        assistance_level="independent",
        adult_confirmed=True
    )

    assert res["learner_code"] == "CHILD-002"
    assert res["target_domain"] == "grammar"
    assert res["deltas"]["grammar"] == -3.0
    assert res["deltas"]["vocabulary"] == 0.0
    assert res["after"]["grammar_score"] == round(initial_gram - 3.0, 1)
    assert res["after"]["vocabulary_score"] == initial_vocab
    assert res["risk_changed"] is False
    assert (learner.screening_risk_level or learner.risk_support_level) == screening_risk_before
    assert "composite_language_index" in res["after"]

def test_profile_updater_success_growth(db_session):
    """
    Tests educational profile promotion when a learner succeeds independently on attempt 1:
    - Base delta: +5.0
    - Easy difficulty: x1.0 = +5.0
    - Vocab task: 100% attributed to primary vocabulary domain (+5.0), grammar delta = 0.0
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-001").first()
    task = db_session.query(Task).filter(Task.category == "vocabulary", Task.base_difficulty == "easy").first()
    assert learner is not None
    assert task is not None

    initial_vocab = learner.vocabulary_score
    initial_gram = learner.grammar_score

    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="success",
        attempt_number=1,
        grammar_errors_count=0,
        assistance_level="independent",
        adult_confirmed=True
    )

    assert res["target_domain"] == "vocabulary"
    assert res["deltas"]["vocabulary"] == 5.0
    assert res["deltas"]["grammar"] == 0.0
    assert res["after"]["vocabulary_score"] == round(initial_vocab + 5.0, 1)
    assert res["after"]["grammar_score"] == initial_gram
    assert res["risk_changed"] is False
