"""
Unit test verifying that 429 quota/rate errors are never classified as native outputs.
"""
from app.model_simplification.quota_manager import GeminiQuotaManager


def test_429_not_counted_as_native():
    qm = GeminiQuotaManager()

    # Record 429 failure
    rec = qm.record_completed(
        request_id="REQ-FAIL-429",
        run_id="RUN-TEST-01",
        dataset_split="locked_test",
        source_group_id="SRC-202",
        support_level="moderate",
        http_status=429,
        execution_status="RATE_LIMIT_FAILED",
        native_output_received=False,
        fallback_used=True,
        resolved_model="gemini-3.5-flash-lite",
        latency_ms=45.0,
        configuration_hash="cfg123",
        output_text="Fallback text from rule engine.",
        error_message="Resource has been exhausted",
    )

    assert rec["native_output_received"] is False
    assert rec["execution_status"] == "RATE_LIMIT_FAILED"
    assert qm.is_already_completed("SRC-202", "moderate") is False
