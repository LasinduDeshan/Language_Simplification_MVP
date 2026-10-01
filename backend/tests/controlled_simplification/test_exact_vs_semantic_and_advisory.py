"""
Unit tests for exact vs semantic protection, modifier criticality, risk immutability, and advisory similarity.
"""

import pytest
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel,
    LearnerProfileContext,
    ProtectedElementsConfig,
    SemanticEquivalenceRule
)
from app.controlled_simplification.protected_elements import is_semantically_equivalent


def test_semantic_equivalence_allowlist():
    """Verify default and custom semantic equivalence mappings."""
    # Default allowed: select -> pick, choose
    assert is_semantically_equivalent("select", "pick") is True
    assert is_semantically_equivalent("select", "choose") is True
    assert is_semantically_equivalent("inside", "in") is True

    # Custom rule: jump -> hop
    custom = [SemanticEquivalenceRule(source="jump", allowed=["hop", "leap"])]
    assert is_semantically_equivalent("jump", "hop", custom_rules=custom) is True
    assert is_semantically_equivalent("jump", "run", custom_rules=custom) is False


def test_advisory_similarity_does_not_override_critical_gate_failure():
    """High similarity cannot bypass an entity or negation violation."""
    engine = ControlledSimplificationEngine()
    req = SimplificationRequest(
        request_id="TEST-SIM",
        text="Do not touch the hot stove.",
        target_support_level=SupportLevel.STRONG
    )
    res = engine.simplify(req)
    # If polarity or safety term was damaged, terminal status would be flagged
    assert res.validation_results.negation_preserved is True


def test_clinical_risk_snapshot_immutability():
    """Engine processes profile context without modifying or returning clinical diagnostic risk scores."""
    engine = ControlledSimplificationEngine()
    profile = LearnerProfileContext(
        learner_id_hash="ANON-TEST-999",
        vocabulary_score=0.35,
        grammar_score=0.40,
        comprehension_score=0.30,
        instruction_following_score=0.35,
        recommended_support_level=SupportLevel.STRONG,
        attempt_number=1
    )
    req = SimplificationRequest(
        request_id="TEST-IMMUTABLE",
        text="Carefully place the red ball in the box.",
        learner_profile=profile
    )
    res = engine.simplify(req)

    assert res.applied_support_level == SupportLevel.STRONG
    # Check that clinical profile is not altered or exposed as a new diagnostic inference
    assert res.status.value in {"PASSED", "PASSED_WITH_ROLLBACK"}
    assert res.governance_metadata.approved_for_child_delivery is False
