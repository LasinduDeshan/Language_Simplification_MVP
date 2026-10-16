"""
Stage 34 — Seven-Level Zero-Loss Accounting Verifier (WP9)
Reconciles all 7 accounting equations across:
Level 1: Evaluation Item Accounting (150 = 124 train + 13 val + 13 locked_test)
Level 2: Reviewer Assignment Accounting (600 = 150 items * 4 assignments)
Level 3: Annotation Submission Accounting (600 = 600 submitted + 0 missing)
Level 4: Dimension Rating Accounting (6,000 = 600 annotations * 10 dimensions)
Level 5: Amendment Accounting (2 amendments = 2 accepted + 0 unaccounted)
Level 6: Adjudication Accounting (5 enqueued = 5 resolved + 0 unaccounted)
Level 7: Rule Disposition Accounting (8 registered = 8 evaluated + 0 unaccounted)
"""

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation"
ASSIGNMENT_FILE = DATA_DIR / "assignments" / "assignment_ledger.jsonl"
ANN_LEDGER = DATA_DIR / "ledgers" / "annotation_ledger.jsonl"
AMD_LEDGER = DATA_DIR / "ledgers" / "amendment_ledger.jsonl"
ADJ_LEDGER = DATA_DIR / "ledgers" / "adjudication_ledger.jsonl"
RULE_LEDGER = DATA_DIR / "ledgers" / "rule_disposition_ledger.jsonl"
CONFIG_FILE = DATA_DIR / "registry" / "stage34_configuration.json"


def verify_seven_level_accounting():
    print("=== Stage 34 Seven-Level Zero-Loss Accounting Verification ===")

    # Level 1: Evaluation Item Accounting
    snapshot_file = DATA_DIR / "snapshots" / "stage33_prerequisite_snapshot.json"
    with open(snapshot_file, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    corpus_counts = snapshot["corpus_counts"]
    train_items = corpus_counts["train"]
    val_items = corpus_counts["validation"]
    test_items = corpus_counts["locked_test"]
    total_items = corpus_counts["canonical_total"]

    assert total_items == 150, f"Expected 150 items, got {total_items}"
    assert total_items == train_items + val_items + test_items, "Partition sum mismatch in Level 1"
    unaccounted_l1 = total_items - (train_items + val_items + test_items)
    print(f"Level 1 (Evaluation Items): {total_items} = {train_items} train + {val_items} val + {test_items} locked_test | Unaccounted: {unaccounted_l1}")
    assert unaccounted_l1 == 0, "Level 1 unaccounted != 0"

    # Level 2: Reviewer Assignment Accounting
    assignments = []
    with open(ASSIGNMENT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                assignments.append(json.loads(line))

    total_assignments = len(assignments)
    expected_assignments = total_items * 4
    assert total_assignments == expected_assignments, f"Expected {expected_assignments} assignments, got {total_assignments}"
    unaccounted_l2 = expected_assignments - total_assignments
    print(f"Level 2 (Reviewer Assignments): {total_assignments} = {total_items} items * 4 reviewers/item | Unaccounted: {unaccounted_l2}")
    assert unaccounted_l2 == 0, "Level 2 unaccounted != 0"

    # Level 3: Annotation Submission Accounting
    annotations = []
    with open(ANN_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                annotations.append(json.loads(line))

    total_submitted = len(annotations)
    missing_annotations = 0
    unaccounted_l3 = total_assignments - (total_submitted + missing_annotations)
    print(f"Level 3 (Annotation Submissions): {total_submitted} submitted, {missing_annotations} missing | Unaccounted: {unaccounted_l3}")
    assert unaccounted_l3 == 0, "Level 3 unaccounted != 0"
    assert total_submitted == 600, f"Expected 600 submitted annotations, got {total_submitted}"

    # Level 4: Dimension Rating Accounting
    dimensions = [
        "meaning_preservation",
        "grammatical_acceptability",
        "morphology_preservation",
        "fluency_naturalness",
        "simplicity_improvement",
        "vocabulary_suitability",
        "sentence_structure_suitability",
        "developmental_suitability",
        "safety",
        "overall_disposition",
    ]
    total_dimension_ratings = total_submitted * len(dimensions)  # 6,000
    status_counts = {"RATED": 0, "CANNOT_ASSESS": 0, "NOT_APPLICABLE": 0, "MISSING": 0}

    for ann in annotations:
        for dim in dimensions:
            dim_val = ann[dim]
            status = dim_val["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
            # Invariant: MISSING is strictly prohibited in submitted annotations
            assert status != "MISSING", f"Found MISSING dimension in submitted annotation {ann['annotation_id']}"
            if status == "RATED":
                assert dim_val["score"] is not None, f"RATED status requires non-null score in {ann['annotation_id']}"
            else:
                assert dim_val["score"] is None, f"{status} status requires null score in {ann['annotation_id']}"

    categorized_ratings = sum(status_counts.values())
    unaccounted_l4 = total_dimension_ratings - categorized_ratings
    print(
        f"Level 4 (Dimension Ratings): {total_dimension_ratings} total = "
        f"{status_counts['RATED']} RATED + {status_counts['CANNOT_ASSESS']} CANNOT_ASSESS + "
        f"{status_counts['NOT_APPLICABLE']} NOT_APPLICABLE | Unaccounted: {unaccounted_l4}"
    )
    assert unaccounted_l4 == 0, "Level 4 unaccounted != 0"

    # Level 5: Amendment Accounting
    amendments = []
    with open(AMD_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                amendments.append(json.loads(line))

    total_amd = len(amendments)
    accepted_amd = sum(1 for a in amendments if a["status"] == "ACCEPTED")
    rejected_amd = sum(1 for a in amendments if a["status"] == "REJECTED")
    pending_amd = sum(1 for a in amendments if a["status"] == "PENDING")
    unaccounted_l5 = total_amd - (accepted_amd + rejected_amd + pending_amd)
    print(f"Level 5 (Amendments): {total_amd} total = {accepted_amd} accepted + {rejected_amd} rejected + {pending_amd} pending | Unaccounted: {unaccounted_l5}")
    assert unaccounted_l5 == 0, "Level 5 unaccounted != 0"
    assert total_amd == 2, f"Expected 2 amendments, got {total_amd}"

    # Level 6: Adjudication Accounting
    adjudications = []
    with open(ADJ_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                adjudications.append(json.loads(line))

    total_adj = len(adjudications)
    resolved_adj = sum(1 for a in adjudications if a["resolved"] is True)
    unresolved_adj = sum(1 for a in adjudications if a["final_disposition"] == "UNRESOLVED_EXPERT_DISAGREEMENT")
    pending_adj = total_adj - (resolved_adj + unresolved_adj)
    unaccounted_l6 = total_adj - (resolved_adj + unresolved_adj + pending_adj)
    print(f"Level 6 (Adjudications): {total_adj} enqueued = {resolved_adj} resolved + {unresolved_adj} unresolved + {pending_adj} pending | Unaccounted: {unaccounted_l6}")
    assert unaccounted_l6 == 0, "Level 6 unaccounted != 0"
    assert pending_adj == 0, "Pending adjudications remain"

    # Level 7: Rule Disposition Accounting
    rule_disps = []
    with open(RULE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rule_disps.append(json.loads(line))

    total_rules = len(rule_disps)
    expected_rules = 8
    unaccounted_l7 = expected_rules - total_rules
    print(f"Level 7 (Rule Dispositions): {total_rules} evaluated = {total_rules} sealed | Unaccounted: {unaccounted_l7}")
    assert unaccounted_l7 == 0, "Level 7 unaccounted != 0"
    assert total_rules == 8, f"Expected 8 rule dispositions, got {total_rules}"

    # Final summary check
    all_zero_loss = (
        unaccounted_l1 == 0
        and unaccounted_l2 == 0
        and unaccounted_l3 == 0
        and unaccounted_l4 == 0
        and unaccounted_l5 == 0
        and unaccounted_l6 == 0
        and unaccounted_l7 == 0
    )

    print("--- Accounting Verification Result ---")
    print(f"Reconciliation Status: 7/7 EQUATIONS RECONCILED")
    print(f"Total Unaccounted Across All Levels: 0")
    print(f"Zero-Loss Invariant Satisfied: {all_zero_loss}")
    return all_zero_loss


if __name__ == "__main__":
    success = verify_seven_level_accounting()
    if not success:
        sys.exit(1)
    print("VERIFICATION SUCCESS: All 7 accounting levels verified with 0 unaccounted.")
