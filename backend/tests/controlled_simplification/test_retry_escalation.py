"""
Tests for progressive retry scaffolding, attempt escalation, and adult support triggers.
"""

import pytest
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel,
    SupportLevelSource,
    TerminalStatus,
    LearnerProfileContext
)
from app.controlled_simplification.retry_adapter import RetryAdapter
from app.controlled_simplification.engine import ControlledSimplificationEngine


def test_retry_scaffolding_progression():
    """Verify progressive hint flags across attempts 1 through 4."""
    meta1 = RetryAdapter.get_scaffolding_metadata(1, SupportLevel.MILD)
    assert meta1.attempt_number == 1
    assert not meta1.visual_hint_flag
    assert not meta1.audio_hint_flag
    assert not meta1.requires_adult_escalation

    meta2 = RetryAdapter.get_scaffolding_metadata(2, SupportLevel.MILD)
    assert meta2.attempt_number == 2
    assert meta2.visual_hint_flag
    assert not meta2.audio_hint_flag
    assert not meta2.requires_adult_escalation

    meta3 = RetryAdapter.get_scaffolding_metadata(3, SupportLevel.MODERATE)
    assert meta3.attempt_number == 3
    assert meta3.visual_hint_flag
    assert meta3.audio_hint_flag
    assert not meta3.requires_adult_escalation

    meta4 = RetryAdapter.get_scaffolding_metadata(4, SupportLevel.STRONG)
    assert meta4.attempt_number == 4
    assert meta4.visual_hint_flag
    assert meta4.audio_hint_flag
    assert meta4.requires_adult_escalation


def test_retry_in_simplification_engine():
    """Verify simplification engine attaches scaffolding metadata and escalates appropriately."""
    engine = ControlledSimplificationEngine()
    
    # Attempt 1
    req1 = SimplificationRequest(
        request_id="REQ-RETRY-001",
        text="Put the red apple in the wooden basket.",
        learner_profile=LearnerProfileContext(
            learner_id_hash="ANON-TEST-001",
            recommended_support_level=SupportLevel.MODERATE,
            attempt_number=1
        )
    )
    res1 = engine.simplify(req1)
    assert res1.scaffolding_metadata.attempt_number == 1
    assert not res1.scaffolding_metadata.requires_adult_escalation

    # Attempt 4 (Exhausted attempts -> adult escalation flag)
    req4 = SimplificationRequest(
        request_id="REQ-RETRY-004",
        text="Put the red apple in the wooden basket.",
        learner_profile=LearnerProfileContext(
            learner_id_hash="ANON-TEST-001",
            recommended_support_level=SupportLevel.MODERATE,
            attempt_number=4
        )
    )
    res4 = engine.simplify(req4)
    assert res4.scaffolding_metadata.attempt_number == 4
    assert res4.scaffolding_metadata.requires_adult_escalation
    assert res4.status == TerminalStatus.ADULT_SUPPORT_REQUIRED
