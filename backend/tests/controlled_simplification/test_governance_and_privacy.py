"""
Unit tests for child delivery governance, fail-closed statuses, and privacy-safe auditing.
"""

import pytest
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel,
    ProtectedElementsConfig,
    LearnerProfileContext
)
from app.controlled_simplification.protected_elements import hash_token
from app.controlled_simplification.audit import PrivacySafeAuditor


def test_draft_governance_metadata_defaults():
    engine = ControlledSimplificationEngine()
    req = SimplificationRequest(
        request_id="TEST-GOV",
        text="Pick the red ball.",
        target_support_level=SupportLevel.MILD
    )
    res = engine.simplify(req)

    assert res.governance_metadata.validation_status == "draft"
    assert res.governance_metadata.approved_for_child_delivery is False
    assert res.governance_metadata.requires_expert_review is True


def test_forbidden_disclosure_hash_rejection():
    """Outputs matching forbidden disclosure hashes must be rejected."""
    engine = ControlledSimplificationEngine()
    secret_token = "secretpassword"
    secret_hash = hash_token(secret_token)

    req = SimplificationRequest(
        request_id="TEST-SECRET",
        text=f"The answer is {secret_token}.",
        target_support_level=SupportLevel.MILD,
        provided_protected_elements=ProtectedElementsConfig(
            forbidden_disclosure_hashes=[secret_hash]
        )
    )
    res = engine.simplify(req)
    assert res.status.value == "REJECTED"


def test_privacy_safe_audit_record_structure():
    engine = ControlledSimplificationEngine()
    req = SimplificationRequest(
        request_id="TEST-AUDIT",
        text="Find the red ball.",
        target_support_level=SupportLevel.MODERATE,
        learner_profile=LearnerProfileContext(
            learner_id_hash="ANON-TEST-12345",
            attempt_number=1
        )
    )
    res = engine.simplify(req)
    audit_record = PrivacySafeAuditor.create_audit_record(res, include_raw_text=False)

    assert audit_record["request_id"] == "TEST-AUDIT"
    assert "original_text_hash" in audit_record
    assert "simplified_text_hash" in audit_record
    assert "_research_raw_text" not in audit_record
