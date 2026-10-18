"""
Regression test verifying the integrity of the Stage 36 Attempt Lineage Execution Receipt.
"""

import json
from pathlib import Path


def test_attempt_lineage_execution_receipt_integrity():
    repo_root = Path(__file__).resolve().parents[3]
    receipt_file = repo_root / "docs" / "stage36_attempt_lineage_execution_receipt.json"

    assert receipt_file.exists(), f"Execution receipt missing at {receipt_file}"

    with open(receipt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["execution_receipt_id"] == "ST36-ATTEMPT-LINEAGE-RECEIPT-V1"
    assert data["database_baseline_verification"]["status"] == "PASSED"
    assert data["stage33_immutability_verification"]["status"] == "PASSED"
    assert data["all_activities_non_repetition_verified"] is True
    assert data["all_activities_validation_passed"] is True
    assert data["governed_activities_count"] == 6

    for act in data["activities"]:
        assert act["all_attempts_distinct"] is True
        # Attempt 1: independent baseline
        assert act["attempt_1"]["independent_performance_measure"] is True
        assert act["attempt_1"]["score_interpretation"] == "INDEPENDENT_BASELINE"
        # Attempt 2: supported
        assert act["attempt_2"]["independent_performance_measure"] is False
        assert act["attempt_2"]["score_interpretation"] == "SUPPORTED_PERFORMANCE"
        # Attempt 3: highly supported
        assert act["attempt_3"]["independent_performance_measure"] is False
        assert act["attempt_3"]["score_interpretation"] == "HIGHLY_SUPPORTED_PERFORMANCE"
        assert act["attempt_3"]["presented_instruction"] != act["attempt_2"]["presented_instruction"]
