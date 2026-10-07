"""
Unit tests for resumable ledger persistence and skipping completed calls.
"""
import json
from pathlib import Path
from app.model_simplification.quota_manager import GeminiQuotaManager


def test_resumable_ledger_workflow(tmp_path: Path):
    ledger_file = tmp_path / "test_ledger.json"
    qm = GeminiQuotaManager(ledger_path=ledger_file)

    # Record completed successful request
    qm.record_completed(
        request_id="REQ-001",
        run_id="RUN-TEST-01",
        dataset_split="validation",
        source_group_id="SRC-101",
        support_level="mild",
        http_status=200,
        execution_status="LIVE_SUCCESS",
        native_output_received=True,
        fallback_used=False,
        resolved_model="gemini-3.5-flash-lite",
        latency_ms=120.5,
        configuration_hash="cfg123",
        output_text="The doctor gave the pill.",
    )

    assert qm.is_already_completed("SRC-101", "mild") is True
    assert qm.is_already_completed("SRC-101", "moderate") is False

    # Simulate process restart and reload
    qm_restarted = GeminiQuotaManager(ledger_path=ledger_file)
    assert qm_restarted.is_already_completed("SRC-101", "mild") is True

    record = qm_restarted.get_completed_record("SRC-101", "mild")
    assert record is not None
    assert record["output_text"] == "The doctor gave the pill."
    assert record["output_hash"] == GeminiQuotaManager.calculate_hash("The doctor gave the pill.")
