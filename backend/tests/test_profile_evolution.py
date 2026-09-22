import pytest
from app.database.db import SessionLocal
from app.database.models import LearnerProfile, Task, ActivitySession, Attempt
from app.personalization.profile_updater import profile_updater
from app.services.session_service import session_service

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
    Tests dynamic profile recalibration when a learner struggles and escalates to adult support:
    - Base delta: -2.5
    - Medium difficulty: x1.2 = -3.0
    - Grammar task: 60% to grammar (-1.8), 10% to vocab (-0.3), 15% to comp (-0.5), 15% to inst (-0.5)
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-002").first()
    task = db_session.query(Task).filter(Task.category == "grammar", Task.base_difficulty == "medium").first()
    assert learner is not None
    assert task is not None

    initial_vocab = learner.vocabulary_score
    initial_gram = learner.grammar_score

    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="adult_support_required",
        attempt_number=3,
        grammar_errors_count=0,
        assistance_level="independent"
    )

    assert res["learner_code"] == "CHILD-002"
    assert res["deltas"]["grammar"] == -1.8
    assert res["deltas"]["vocabulary"] == -0.3
    assert res["after"]["grammar_score"] == round(initial_gram - 1.8, 1)
    assert res["after"]["vocabulary_score"] == round(initial_vocab - 0.3, 1)
    assert "composite_language_index" in res["after"]

def test_profile_updater_success_growth(db_session):
    """
    Tests dynamic profile promotion when a learner succeeds independently on attempt 1:
    - Base delta: +5.0
    - Vocab task: 60% to vocab, 10% to gram
    """
    learner = db_session.query(LearnerProfile).filter(LearnerProfile.learner_code == "CHILD-001").first()
    task = db_session.query(Task).filter(Task.category == "vocabulary", Task.base_difficulty == "easy").first()
    assert learner is not None
    assert task is not None

    initial_vocab = learner.vocabulary_score
    res = profile_updater.update_profile_after_session(
        db=db_session,
        learner=learner,
        task=task,
        session_final_outcome="success",
        attempt_number=1,
        grammar_errors_count=0,
        assistance_level="independent"
    )

    assert res["deltas"]["vocabulary"] > 0
    assert res["after"]["vocabulary_score"] > initial_vocab
