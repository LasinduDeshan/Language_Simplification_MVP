"""
Stage 34 — Eight-Level Zero-Loss Accounting Verifier (WP9)
Reconciles all 8 accounting equations across:
Level 1: Reviewer Accounting:
         Recruited = Qualified + RetrainingRequired + Excluded + Withdrawn + Unaccounted
         (7 = 6 qualified + 0 retraining + 1 excluded/quarantined + 0 withdrawn + 0 unaccounted)
Level 2: Evaluation Item Accounting:
         CanonicalItems = Train + Validation + LockedTest + Unaccounted
         (150 = 124 + 13 + 13 + 0)
Level 3: Reviewer Assignment Accounting:
         Assignments = Items * 4 + Unaccounted
         (600 = 150 * 4 + 0)
Level 4: Annotation Submission Accounting:
         Submissions = Submitted + Missing + Unaccounted
         (600 = 600 + 0 + 0)
Level 5: Dimension Rating Accounting:
         DimensionRatings = RATED + CANNOT_ASSESS + NOT_APPLICABLE + MISSING + Unaccounted
         (6,000 = 5,140 + 544 + 316 + 0 + 0)
Level 6: Amendment Accounting:
         Amendments = Accepted + Rejected + Pending + Unaccounted
         (2 = 2 + 0 + 0 + 0)
Level 7: Adjudication Accounting:
         AdjudicationQueue = Resolved + UnresolvedExpertDisagreement + Pending + Excluded + Unaccounted
         (5 = 5 + 0 + 0 + 0 + 0)
Level 8: Rule Disposition Accounting:
         EvaluatedRules = SupportedForResearch + SupportedWithConstraints + RevisionRequired +
                          Rejected + InsufficientEvidence + UnresolvedDisagreement + Unaccounted
         (8 = 8 + 0 + 0 + 0 + 0 + 0 + 0) with sealed=True verified separately.
"""

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from app.datasets.sinhala_expert_validation.enums import RuleDisposition, TrainingStatus
from scripts.stage34.build_annotation_items import setup_panel

DATA_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation"
ASSIGNMENT_FILE = DATA_DIR / "assignments" / "assignment_ledger.jsonl"
ANN_LEDGER = DATA_DIR / "ledgers" / "annotation_ledger.jsonl"
AMD_LEDGER = DATA_DIR / "ledgers" / "amendment_ledger.jsonl"
ADJ_LEDGER = DATA_DIR / "ledgers" / "adjudication_ledger.jsonl"
RULE_LEDGER = DATA_DIR / "ledgers" / "rule_disposition_ledger.jsonl"
CONFIG_FILE = DATA_DIR / "registry" / "stage34_configuration.json"


def verify_eight_level_accounting():
    print("=== Stage 34 Eight-Level Zero-Loss Accounting Verification ===")

    # Level 1: Reviewer Accounting
    # Recruited = Qualified + RetrainingRequired + Excluded + Withdrawn + Unaccounted
    registry = setup_panel()
    all_reviewers = registry.list_reviewers(qualified_only=False)
    recruited = len(all_reviewers)
    qualified = sum(1 for r in all_reviewers if r.training_status == TrainingStatus.QUALIFIED)
    retraining = sum(1 for r in all_reviewers if r.training_status == TrainingStatus.RETRAINING_REQUIRED)
    excluded = sum(
        1 for r in all_reviewers
        if r.is_project_team_member or r.training_status == TrainingStatus.EXCLUDED
    )
    withdrawn = sum(1 for r in all_reviewers if r.training_status == TrainingStatus.WITHDRAWN)
    unaccounted_l1 = recruited - (qualified + retraining + excluded + withdrawn)

    # Panel diversity breakdown
    panel_check = registry.verify_panel_composition()
    first_pass_count = panel_check["linguists_count"] + panel_check["educators_count"] + panel_check["child_dev_count"]
    adjudicator_count = panel_check["adjudicator_count"]
    total_unique_panel = panel_check["unique_qualified_count"]

    print(
        f"Level 1 (Reviewer Panel): {recruited} recruited = {qualified} qualified + "
        f"{retraining} retraining + {excluded} excluded/quarantined + {withdrawn} withdrawn | Unaccounted: {unaccounted_l1}"
    )
    print(
        f"         Panel Structure: {first_pass_count} first-pass raters (2 linguists, 2 educators, 1 child-dev) + "
        f"{adjudicator_count} independent adjudicator = {total_unique_panel} unique panel members"
    )
    assert unaccounted_l1 == 0, "Level 1 unaccounted != 0"
    assert qualified >= 6, f"Expected at least 6 qualified reviewers, got {qualified}"
    assert panel_check["is_valid"] is True, "Panel composition check failed"

    # Level 2: Evaluation Item Accounting
    snapshot_file = DATA_DIR / "snapshots" / "stage33_prerequisite_snapshot.json"
    with open(snapshot_file, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    corpus_counts = snapshot["corpus_counts"]
    train_items = corpus_counts["train"]
    val_items = corpus_counts["validation"]
    test_items = corpus_counts["locked_test"]
    total_items = corpus_counts["canonical_total"]

    assert total_items == 150, f"Expected 150 items, got {total_items}"
    assert total_items == train_items + val_items + test_items, "Partition sum mismatch in Level 2"
    unaccounted_l2 = total_items - (train_items + val_items + test_items)
    print(f"Level 2 (Evaluation Items): {total_items} = {train_items} train + {val_items} val + {test_items} locked_test | Unaccounted: {unaccounted_l2}")
    assert unaccounted_l2 == 0, "Level 2 unaccounted != 0"

    # Level 3: Reviewer Assignment Accounting
    assignments = []
    with open(ASSIGNMENT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                assignments.append(json.loads(line))

    total_assignments = len(assignments)
    expected_assignments = total_items * 4
    assert total_assignments == expected_assignments, f"Expected {expected_assignments} assignments, got {total_assignments}"
    unaccounted_l3 = expected_assignments - total_assignments
    print(f"Level 3 (Reviewer Assignments): {total_assignments} = {total_items} items * 4 reviewers/item | Unaccounted: {unaccounted_l3}")
    assert unaccounted_l3 == 0, "Level 3 unaccounted != 0"

    # Level 4: Annotation Submission Accounting
    annotations = []
    with open(ANN_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                annotations.append(json.loads(line))

    total_submitted = len(annotations)
    missing_annotations = 0
    unaccounted_l4 = total_assignments - (total_submitted + missing_annotations)
    print(f"Level 4 (Annotation Submissions): {total_submitted} submitted, {missing_annotations} missing | Unaccounted: {unaccounted_l4}")
    assert unaccounted_l4 == 0, "Level 4 unaccounted != 0"
    assert total_submitted == 600, f"Expected 600 submitted annotations, got {total_submitted}"

    # Level 5: Dimension Rating Accounting
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
            assert status != "MISSING", f"Found MISSING dimension in submitted annotation {ann['annotation_id']}"
            if status == "RATED":
                assert dim_val["score"] is not None, f"RATED status requires non-null score in {ann['annotation_id']}"
            else:
                assert dim_val["score"] is None, f"{status} status requires null score in {ann['annotation_id']}"

    categorized_ratings = sum(status_counts.values())
    unaccounted_l5 = total_dimension_ratings - categorized_ratings
    print(
        f"Level 5 (Dimension Ratings): {total_dimension_ratings} total = "
        f"{status_counts['RATED']} RATED + {status_counts['CANNOT_ASSESS']} CANNOT_ASSESS + "
        f"{status_counts['NOT_APPLICABLE']} NOT_APPLICABLE + {status_counts['MISSING']} MISSING | Unaccounted: {unaccounted_l5}"
    )
    assert unaccounted_l5 == 0, "Level 5 unaccounted != 0"

    # Level 6: Amendment Accounting
    amendments = []
    with open(AMD_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                amendments.append(json.loads(line))

    total_amd = len(amendments)
    accepted_amd = sum(1 for a in amendments if a["status"] == "ACCEPTED")
    rejected_amd = sum(1 for a in amendments if a["status"] == "REJECTED")
    pending_amd = sum(1 for a in amendments if a["status"] == "PENDING")
    unaccounted_l6 = total_amd - (accepted_amd + rejected_amd + pending_amd)
    print(f"Level 6 (Amendments): {total_amd} total = {accepted_amd} accepted + {rejected_amd} rejected + {pending_amd} pending | Unaccounted: {unaccounted_l6}")
    assert unaccounted_l6 == 0, "Level 6 unaccounted != 0"
    assert total_amd == 2, f"Expected 2 amendments, got {total_amd}"

    # Level 7: Adjudication Accounting
    adjudications = []
    with open(ADJ_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                adjudications.append(json.loads(line))

    total_adj = len(adjudications)
    resolved_adj = sum(1 for a in adjudications if a["resolved"] is True)
    unresolved_adj = sum(1 for a in adjudications if a["final_disposition"] == "UNRESOLVED_EXPERT_DISAGREEMENT")
    pending_adj = sum(1 for a in adjudications if not a["resolved"])
    excluded_adj = 0
    unaccounted_l7 = total_adj - (resolved_adj + unresolved_adj + pending_adj + excluded_adj)
    print(f"Level 7 (Adjudications): {total_adj} enqueued = {resolved_adj} resolved + {unresolved_adj} unresolved + {pending_adj} pending + {excluded_adj} excluded | Unaccounted: {unaccounted_l7}")
    assert unaccounted_l7 == 0, "Level 7 unaccounted != 0"
    assert pending_adj == 0, "Pending adjudications remain"

    # Level 8: Rule Disposition Accounting
    # EvaluatedRules = SupportedForResearch + SupportedWithConstraints + RevisionRequired +
    #                  Rejected + InsufficientEvidence + UnresolvedDisagreement + Unaccounted
    rule_disps = []
    with open(RULE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rule_disps.append(json.loads(line))

    total_rules = len(rule_disps)
    sup_res = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.SUPPORTED_FOR_FURTHER_RESEARCH.value)
    sup_con = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.SUPPORTED_WITH_CONSTRAINTS.value)
    rev_req = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.REVISION_REQUIRED.value)
    rej_rule = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.REJECT_RULE_OR_OUTPUT_PATTERN.value)
    insuf_ev = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.INSUFFICIENT_EXPERT_EVIDENCE.value)
    unres_dis = sum(1 for r in rule_disps if r["disposition"] == RuleDisposition.UNRESOLVED_EXPERT_DISAGREEMENT.value)
    unaccounted_l8 = total_rules - (sup_res + sup_con + rev_req + rej_rule + insuf_ev + unres_dis)

    # Verify sealed property separately
    sealed_count = sum(1 for r in rule_disps if r.get("sealed") is True)
    assert sealed_count == total_rules, f"Not all rules are marked sealed=True: {sealed_count}/{total_rules}"

    print(
        f"Level 8 (Rule Dispositions): {total_rules} evaluated = {sup_res} SupportedForResearch + "
        f"{sup_con} SupportedWithConstraints + {rev_req} RevisionRequired + {rej_rule} Rejected + "
        f"{insuf_ev} InsufficientEvidence + {unres_dis} UnresolvedDisagreement | Unaccounted: {unaccounted_l8}"
    )
    print(f"         Sealed Flag: {sealed_count}/{total_rules} rules sealed (sealed=true)")
    assert unaccounted_l8 == 0, "Level 8 unaccounted != 0"
    assert total_rules == 8, f"Expected 8 rule dispositions, got {total_rules}"

    # Final summary check across all 8 levels
    all_zero_loss = (
        unaccounted_l1 == 0
        and unaccounted_l2 == 0
        and unaccounted_l3 == 0
        and unaccounted_l4 == 0
        and unaccounted_l5 == 0
        and unaccounted_l6 == 0
        and unaccounted_l7 == 0
        and unaccounted_l8 == 0
    )

    print("--- Accounting Verification Result ---")
    print(f"Reconciliation Status: 8/8 EQUATIONS RECONCILED")
    print(f"Total Unaccounted Across All Levels: 0")
    print(f"Zero-Loss Invariant Satisfied: {all_zero_loss}")
    return all_zero_loss


# Backwards compatibility alias
verify_seven_level_accounting = verify_eight_level_accounting


if __name__ == "__main__":
    success = verify_eight_level_accounting()
    if not success:
        sys.exit(1)
    print("VERIFICATION SUCCESS: All 8 accounting levels verified with 0 unaccounted.")
