"""
Unit tests for support level precedence hierarchy and attempt escalation.
"""

import pytest
from app.controlled_simplification.schemas import (
    SupportLevel,
    SupportLevelSource,
    LearnerProfileContext
)
from app.controlled_simplification.support_controller import SupportController


def test_authorized_explicit_request_precedence():
    """Explicit authorized request overrides learner profile recommendation."""
    profile = LearnerProfileContext(
        recommended_support_level=SupportLevel.STRONG,
        attempt_number=1
    )
    level, source, override = SupportController.resolve_support_level(
        target_support_level=SupportLevel.MILD,
        learner_profile=profile,
        attempt_number=1
    )
    assert level == SupportLevel.MILD
    assert source == SupportLevelSource.AUTHORIZED_REQUEST
    assert override is None


def test_learner_profile_fallback_when_no_explicit_request():
    """If no target support level is passed, use profile recommendation."""
    profile = LearnerProfileContext(
        recommended_support_level=SupportLevel.STRONG,
        attempt_number=1
    )
    level, source, override = SupportController.resolve_support_level(
        target_support_level=None,
        learner_profile=profile,
        attempt_number=1
    )
    assert level == SupportLevel.STRONG
    assert source == SupportLevelSource.LEARNER_PROFILE_RECOMMENDATION


def test_attempt_2_escalation():
    """Attempt 2 escalates Mild to Moderate, and Moderate to Strong."""
    # Mild -> Moderate
    l1, s1, o1 = SupportController.resolve_support_level(
        target_support_level=SupportLevel.MILD,
        learner_profile=None,
        attempt_number=2
    )
    assert l1 == SupportLevel.MODERATE
    assert s1 == SupportLevelSource.ATTEMPT_ESCALATION

    # Moderate -> Strong
    l2, s2, o2 = SupportController.resolve_support_level(
        target_support_level=SupportLevel.MODERATE,
        learner_profile=None,
        attempt_number=2
    )
    assert l2 == SupportLevel.STRONG
    assert s2 == SupportLevelSource.ATTEMPT_ESCALATION


def test_attempt_3_maximum_strong():
    """Attempt 3 escalates any tier to Strong."""
    l, s, o = SupportController.resolve_support_level(
        target_support_level=SupportLevel.MILD,
        learner_profile=None,
        attempt_number=3
    )
    assert l == SupportLevel.STRONG
    assert s == SupportLevelSource.ATTEMPT_ESCALATION
    assert "Escalated to Strong" in o
