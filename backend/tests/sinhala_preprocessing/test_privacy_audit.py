"""
Tests for Stage 30 Privacy-Safe Audit Logging.
"""

from app.sinhala_preprocessing.audit import log_audit_event

def test_audit_event_contains_no_raw_text():
    raw_sensitive_text = "සංවේදී ළමා විස්තර"
    event = log_audit_event(
        record_id="REC-001",
        raw_sha256="abc123sha",
        normalized_sha256="def456sha",
        final_disposition="PASSED",
        disposition_reason_code="CANONICAL_NFC",
        quality_flags=[],
        operation_count=1,
        sentence_count=1,
        token_count=3,
        grapheme_count=10
    )

    event_str = str(event)
    assert raw_sensitive_text not in event_str
    assert "raw_sha256" in event
    assert "normalized_sha256" in event
    assert event["approved_for_child_delivery"] is False
