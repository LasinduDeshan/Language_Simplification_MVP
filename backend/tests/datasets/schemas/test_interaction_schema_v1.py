import pytest
from app.datasets.interaction_dataset.schemas import PrivateInteractionRecordV1
from app.datasets.common.enums import (
    ActivityOwner, PrimaryDomain, SupportLevel, ResponseMode, Outcome
)

def test_valid_private_interaction_record():
    rec = PrivateInteractionRecordV1(
        interaction_id="INT-20260923-000001",
        learner_id="CHILD-002",
        session_id="SESSION-UUID-001",
        activity_id="C3-EN-GRAM-0001",
        activity_owner=ActivityOwner.COMPONENT_3_LANGUAGE,
        primary_domain=PrimaryDomain.GRAMMAR,
        attempt_number=1,
        support_level_used=SupportLevel.MODERATE,
        response_mode=ResponseMode.MANUAL,
        response_text_private="the dog runs",
        outcome=Outcome.CORRECT,
        score_before=50.0,
        score_delta=0.5,
        score_after=50.5,
        screening_risk_modified=False
    )
    assert rec.interaction_id == "INT-20260923-000001"
    assert rec.screening_risk_modified is False

def test_screening_risk_modified_true_raises():
    with pytest.raises(ValueError, match="screening_risk_modified must always be false"):
        PrivateInteractionRecordV1(
            interaction_id="INT-20260923-000001",
            learner_id="CHILD-002",
            session_id="SESSION-UUID-001",
            activity_id="C3-EN-GRAM-0001",
            primary_domain=PrimaryDomain.GRAMMAR,
            screening_risk_modified=True  # Disallowed
        )

def test_score_arithmetic_inconsistency_raises():
    with pytest.raises(ValueError, match="Score arithmetic inconsistent"):
        PrivateInteractionRecordV1(
            interaction_id="INT-20260923-000001",
            learner_id="CHILD-002",
            session_id="SESSION-UUID-001",
            activity_id="C3-EN-GRAM-0001",
            primary_domain=PrimaryDomain.GRAMMAR,
            score_before=50.0,
            score_delta=5.0,
            score_after=60.0  # Incorrect sum
        )
