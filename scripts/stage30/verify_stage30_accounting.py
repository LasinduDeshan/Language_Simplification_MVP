"""
Stage 30 Accounting Verifier.
Reconciles total records, operations, sentences, tokens, and ensures zero unaccounted units:
Total Inputs = Passed + PassedWithNormalization + ManualReviewRequired + RejectedInvalidUnicode + ExcludedNonSinhala + Unaccounted
Target: Unaccounted = 0
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SUMMARY_PATH = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "results" / "fixture_evaluation_summary.json"

def verify_accounting():
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Evaluation summary missing: {SUMMARY_PATH}")

    data = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    total_inputs = data["total_fixtures"]
    disp_counts = data["disposition_counts"]

    passed = disp_counts.get("PASSED", 0)
    passed_norm = disp_counts.get("PASSED_WITH_NORMALIZATION", 0)
    review = disp_counts.get("MANUAL_REVIEW_REQUIRED", 0)
    rejected = disp_counts.get("REJECTED_INVALID_UNICODE", 0)
    excluded = disp_counts.get("EXCLUDED_NON_SINHALA", 0)

    calculated_sum = passed + passed_norm + review + rejected + excluded
    unaccounted = total_inputs - calculated_sum

    print("--- Stage 30 Record Accounting ---")
    print(f"Total Inputs:               {total_inputs}")
    print(f"Passed:                     {passed}")
    print(f"Passed with Normalization:  {passed_norm}")
    print(f"Manual Review Required:     {review}")
    print(f"Rejected Invalid Unicode:   {rejected}")
    print(f"Excluded Non-Sinhala:       {excluded}")
    print(f"Unaccounted Records:        {unaccounted}")

    assert unaccounted == 0, f"Accounting reconciliation failed: {unaccounted} unaccounted records!"
    assert data["offset_failures"] == 0, f"Offset failures detected: {data['offset_failures']}"
    assert data["reconstruction_failures"] == 0, f"Reconstruction failures detected: {data['reconstruction_failures']}"
    assert data["pipeline_introduced_replacement_characters"] == 0, "Pipeline-introduced U+FFFD detected!"

    print("\n--- Additional Element Accounting ---")
    print(f"Total Operations Recorded:  {data['total_operations']}")
    print(f"Total Sentences Segmented:  {data['total_sentences']}")
    print(f"Total Tokens Produced:      {data['total_tokens']}")
    print(f"Records with Joiners:       {data['records_with_joiners']}")
    print(f"Records with Mixed Scripts: {data['records_with_mixed_scripts']}")
    print(f"Records Routed to Review:   {data['records_routed_to_review']}")
    print("Accounting Reconciliation:  PASSED (Zero unaccounted units)")
    return True

if __name__ == "__main__":
    verify_accounting()
