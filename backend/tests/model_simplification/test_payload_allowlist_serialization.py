"""
Tests for Privacy Filter & Strict Provider Payload Allowlist.
Verifies that forbidden fields (PII, answer_boundary_ref, answers, hashes, learner IDs, scores) are strictly blocked.
"""

import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElements,
    SupportLevel
)
from app.model_simplification.privacy_filter import (
    serialize_provider_payload,
    sanitize_text,
    SanitizationError,
    FORBIDDEN_PAYLOAD_KEYS
)


def test_payload_allowlist_serialization_clean():
    req = ModelGenerationRequest(
        request_id="GENREQ-001",
        text="Identify the blue square before placing the yellow block inside the bucket.",
        language="en",
        support_level=SupportLevel.STRONG,
        protected_elements=ProtectedElements(
            exact_preservation=["blue", "square", "yellow", "block", "bucket"],
            semantic_equivalence_refs=["SEMREF-001"],
            answer_boundary_ref="ANSBOUND-SECRET-999"  # Server-side only
        )
    )

    payload = serialize_provider_payload(req)
    
    # 1. Verify Allowed Fields
    assert payload["text"] == req.text
    assert payload["language"] == "en"
    assert payload["support_level"] == "strong"
    assert payload["protected_elements"]["exact_preservation"] == ["blue", "square", "yellow", "block", "bucket"]
    
    # 2. Verify Forbidden Fields are ABSENT
    payload_str = str(payload)
    assert "ANSBOUND-SECRET-999" not in payload_str
    assert "answer_boundary_ref" not in payload
    assert "screening_risk" not in payload
    assert "learner_id" not in payload


def test_sanitization_strips_pii():
    text_with_pii = "Contact teacher at john.doe@school.edu or call 555-123-4567 for LEARNER-XYZ-1234."
    cleaned = sanitize_text(text_with_pii)
    assert "john.doe@school.edu" not in cleaned
    assert "555-123-4567" not in cleaned
    assert "LEARNER-XYZ-1234" not in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "[REDACTED_PHONE]" in cleaned
    assert "[REDACTED_ID]" in cleaned


def test_sanitization_error_on_empty():
    req = ModelGenerationRequest(
        request_id="GENREQ-EMPTY",
        text="   ",
        support_level=SupportLevel.MILD
    )
    with pytest.raises(SanitizationError):
        serialize_provider_payload(req)
