import pytest
from datetime import datetime
from app.datasets.interaction_dataset.export_schemas import DeidentifiedInteractionExportV1
from app.datasets.common.enums import PrimaryDomain, SupportLevel, ResponseMode, Outcome

def test_valid_deidentified_interaction_export():
    exp = DeidentifiedInteractionExportV1(
        interaction_id="INT-20260923-000001",
        learner_id="CHILD-002",
        activity_id="C3-EN-GRAM-0001",
        primary_domain=PrimaryDomain.GRAMMAR,
        occurred_at=datetime.utcnow(),
        attempt_number=1,
        support_level_used=SupportLevel.MODERATE,
        response_mode=ResponseMode.MANUAL,
        outcome=Outcome.CORRECT,
        response_time_ms=5000,
        score_delta=0.5,
        local_preliminary_trend="stable_positive"
    )
    assert exp.interaction_id == "INT-20260923-000001"
    
    # Verify raw response text cannot be injected into allowlist export model
    dump = exp.model_dump()
    assert "response_text_private" not in dump
    assert "raw_notes" not in dump
