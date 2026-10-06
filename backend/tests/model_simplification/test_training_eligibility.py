"""
Unit tests for Stage 26 Group-Safe Training Eligibility and Exclusion Precedence.
"""
import json
import pytest
from pathlib import Path
from app.model_simplification.training.eligibility import (
    GroupSafeEligibilityAuditor,
    DISPOSITION_DIRECT_REFORMULATION,
    DISPOSITION_SOURCE_GROUP_REFORMULATION,
    DISPOSITION_NON_DEV_SPLIT,
    DISPOSITION_ELIGIBLE_INTERNAL_TRAINING,
)


@pytest.fixture
def auditor():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    return GroupSafeEligibilityAuditor(repo_root=repo_root)


def test_dynamic_recalculation_matches_issue_register(auditor):
    result = auditor.run_audit()
    rec = result["reconciliation"]

    assert rec["total_pairs"] == 900
    assert rec["directly_flagged_reformulation_pairs"] == 326
    assert rec["dynamically_recalculated_contaminated_groups"] == 203
    # 203 groups * 3 tiers = 609 pairs
    assert rec["total_group_reformulation_excluded_pairs"] == 609
    assert rec["eligible_internal_training_groups"] == 70
    assert rec["eligible_internal_training_pairs"] == 210
    assert rec["mutually_exclusive_sum"] == 900


def test_group_safe_exclusion_excludes_entire_source_group(auditor):
    result = auditor.run_audit()
    pair_disps = result["pair_dispositions"]

    # Map groups to their member pair dispositions
    group_disps = {}
    for p in pair_disps:
        gid = p["source_group_id"]
        if gid not in group_disps:
            group_disps[gid] = []
        group_disps[gid].append(p["disposition"])

    for gid, disps in group_disps.items():
        if DISPOSITION_DIRECT_REFORMULATION in disps:
            # If any pair in group was directly flagged, all pairs in group must be excluded
            for d in disps:
                assert d in [DISPOSITION_DIRECT_REFORMULATION, DISPOSITION_SOURCE_GROUP_REFORMULATION]
                assert d != DISPOSITION_ELIGIBLE_INTERNAL_TRAINING


def test_eligibility_disposition_precedence(auditor):
    result = auditor.run_audit()
    disps = result["reconciliation"]["disposition_breakdown"]

    assert disps[DISPOSITION_DIRECT_REFORMULATION] == 326
    assert disps[DISPOSITION_SOURCE_GROUP_REFORMULATION] == 283
    assert disps[DISPOSITION_NON_DEV_SPLIT] == 81
    assert disps[DISPOSITION_ELIGIBLE_INTERNAL_TRAINING] == 210
    assert sum(disps.values()) == 900


def test_complete_three_tier_group_requirement(auditor):
    result = auditor.run_audit()
    eligible_groups = result["eligible_groups"]
    pair_disps = {p["pair_id"]: p for p in result["pair_dispositions"]}

    assert len(eligible_groups) == 70

    for eg in eligible_groups:
        pair_ids = eg["pair_ids"]
        assert len(pair_ids) == 3
        tiers = {pair_disps[pid]["support_level"] for pid in pair_ids}
        assert tiers == {"mild", "moderate", "strong"}


def test_original_corpus_immutability(auditor):
    result = auditor.run_audit()
    assert result["source_records_modified"] is False
    for eg in result["eligible_groups"]:
        assert eg["source_record_modified"] is False
        assert eg["internal_training_decision"] == "approved_for_pilot_fine_tuning"
