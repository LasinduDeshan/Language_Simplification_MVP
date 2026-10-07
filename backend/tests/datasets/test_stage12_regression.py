import pytest
from app.database.db import SessionLocal
from app.database.models import LearnerProfile, Task
from app.personalization.profile_updater import profile_updater

def test_stage12_educational_domains_update_properly():
    db = SessionLocal()
    try:
        # Create a test learner profile
        profile = LearnerProfile(
            learner_code="CHILD-STAGE13-TEST",
            age=6,
            screening_risk_level="low",
            recommended_support_level="mild",
            risk_support_level="low",
            vocabulary_score=50.0,
            grammar_score=50.0,
            comprehension_score=50.0,
            instruction_following_score=50.0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        task = db.query(Task).filter(Task.category == "vocabulary").first()
        assert task is not None

        # Ensure screening_risk_level is read-only and remains "low"
        initial_risk = profile.screening_risk_level
        assert initial_risk == "low"
        
        # Test vocabulary activity update
        res = profile_updater.update_profile_after_session(
            db=db,
            learner=profile,
            task=task,
            session_final_outcome="success",
            attempt_number=1,
            assistance_level="independent",
            adult_confirmed=True
        )
        db.refresh(profile)
        assert profile.vocabulary_score > 50.0
        assert profile.screening_risk_level == initial_risk, "Screening risk level must not change during educational activity!"

        # Clean up test profile
        db.delete(profile)
        db.commit()
    finally:
        db.close()
