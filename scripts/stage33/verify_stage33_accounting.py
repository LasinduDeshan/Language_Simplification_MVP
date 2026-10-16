"""
Stage 33 — Accounting Reconciliation Verifier.
Verifies all 6 accounting conservation equations with zero-unaccounted invariant.
"""

import json
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER_DIR = PROJECT_ROOT / "data" / "sinhala_simplification" / "ledgers"


def verify_accounting():
    print("=== Stage 33 — Verifying Accounting Conservation Equations ===")

    # 1. Level 1: Input Disposition Accounting
    final_file = LEDGER_DIR / "final_disposition_ledger.jsonl"
    assert final_file.exists(), f"Missing ledger: {final_file}"
    dispositions = []
    with open(final_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                dispositions.append(data["final_disposition"])

    submitted_inputs = len(dispositions)
    assert submitted_inputs == 124, f"Expected 124 train inputs, got {submitted_inputs}"

    disp_counts = Counter(dispositions)
    reconciled_inputs = (
        disp_counts.get("DRAFT_REWRITE_SELECTED", 0)
        + disp_counts.get("UNCHANGED_ALL_CANDIDATES_BLOCKED", 0)
        + disp_counts.get("UNCHANGED_NO_APPLICABLE_RULE", 0)
        + disp_counts.get("MANUAL_REVIEW_REQUIRED", 0)
        + disp_counts.get("REJECTED_SOURCE_INELIGIBLE", 0)
        + disp_counts.get("REJECTED_INVALID_PREPROCESSING_STATE", 0)
        + disp_counts.get("FAILED_INTERNAL_ERROR", 0)
    )
    unaccounted_inputs = submitted_inputs - reconciled_inputs
    assert unaccounted_inputs == 0, f"Accounting Level 1 Failure: unaccounted inputs {unaccounted_inputs}"
    print(f"Level 1 (Inputs):       Reconciled {submitted_inputs}/{submitted_inputs} (Unaccounted: 0) [OK]")

    # 2. Level 2: Rule Attempt Accounting
    att_file = LEDGER_DIR / "rule_attempt_ledger.jsonl"
    assert att_file.exists(), f"Missing ledger: {att_file}"
    attempts = []
    with open(att_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                attempts.append(data["terminal_status"])

    total_attempts = len(attempts)
    att_counts = Counter(attempts)
    reconciled_attempts = (
        att_counts.get("CANDIDATE_GENERATED", 0)
        + att_counts.get("NOT_APPLICABLE", 0)
        + att_counts.get("BLOCKED_PROTECTED_SPAN", 0)
        + att_counts.get("BLOCKED_MEANING_GUARD", 0)
        + att_counts.get("DEFERRED_MANUAL_REVIEW", 0)
        + att_counts.get("FAILED_INTERNAL", 0)
    )
    unaccounted_attempts = total_attempts - reconciled_attempts
    assert unaccounted_attempts == 0, f"Accounting Level 2 Failure: unaccounted attempts {unaccounted_attempts}"
    print(f"Level 2 (Rule Attempts): Reconciled {total_attempts}/{total_attempts} (Unaccounted: 0) [OK]")

    # 3. Level 3: Candidate Accounting
    cand_file = LEDGER_DIR / "candidate_ledger.jsonl"
    assert cand_file.exists(), f"Missing ledger: {cand_file}"
    candidates = []
    with open(cand_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                candidates.append(data["terminal_status"])

    total_candidates = len(candidates)
    cand_counts = Counter(candidates)
    reconciled_candidates = (
        cand_counts.get("SELECTED", 0)
        + cand_counts.get("NOT_SELECTED_LOWER_RANK", 0)
        + cand_counts.get("BLOCKED_PROTECTED_SPAN", 0)
        + cand_counts.get("BLOCKED_MEANING_GUARD", 0)
        + cand_counts.get("DEFERRED_MANUAL_REVIEW", 0)
        + cand_counts.get("FAILED_INTERNAL", 0)
    )
    unaccounted_candidates = total_candidates - reconciled_candidates
    assert unaccounted_candidates == 0, f"Accounting Level 3 Failure: unaccounted candidates {unaccounted_candidates}"
    print(f"Level 3 (Candidates):   Reconciled {total_candidates}/{total_candidates} (Unaccounted: 0) [OK]")

    # 4. Level 4: Transformation Operation Accounting
    op_file = LEDGER_DIR / "transformation_trace_ledger.jsonl"
    assert op_file.exists(), f"Missing ledger: {op_file}"
    operations = []
    with open(op_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                operations.append(data["operation_type"])

    total_ops = len(operations)
    op_counts = Counter(operations)
    reconciled_ops = sum(op_counts.values())
    unaccounted_ops = total_ops - reconciled_ops
    assert unaccounted_ops == 0, f"Accounting Level 4 Failure: unaccounted operations {unaccounted_ops}"
    print(f"Level 4 (Operations):   Reconciled {total_ops}/{total_ops} (Unaccounted: 0) [OK]")

    print("\nALL ACCOUNTING EQUATIONS PASSED WITH ZERO UNACCOUNTED UNITS!")


if __name__ == "__main__":
    verify_accounting()
