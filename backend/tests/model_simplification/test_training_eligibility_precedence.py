"""
Tests for Training Eligibility Precedence and Complete Group Invariant.
"""

import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent.parent


def test_training_eligibility_manifest_precedence():
    manifest_file = repo_root / "data" / "model_simplification" / "manifests" / "stage26_training_eligibility_manifest.json"
    assert manifest_file.exists(), "Training eligibility manifest must exist."

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["total_pairs_scanned"] == 900
    assert manifest["total_groups_scanned"] == 300

    # Mutually exclusive pair balance
    pair_acc = manifest["pair_accounting"]
    assert sum(pair_acc.values()) == 900
    assert pair_acc["task_reformulation_excluded"] == 326
    assert pair_acc["source_group_reformulation_excluded"] == 195
    assert pair_acc["non_development_split_excluded"] == 169
    assert pair_acc["eligible_for_internal_model_development"] == 210

    # Mutually exclusive group balance
    group_acc = manifest["group_accounting"]
    assert sum(group_acc.values()) == 300
    assert group_acc["task_reformulation_group_excluded"] == 203
    assert group_acc["non_development_group_excluded"] == 27
    assert group_acc["eligible_internal_training_group"] == 70


def test_complete_group_invariant():
    manifest_file = repo_root / "data" / "model_simplification" / "manifests" / "stage26_training_eligibility_manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    records = manifest["records"]
    eligible_records = [r for r in records if r["primary_eligibility_disposition"] == "eligible_for_internal_model_development"]
    
    # 210 pristine pairs in 70 complete training groups
    assert len(eligible_records) == 210

    # Group grouping
    group_map = {}
    for r in eligible_records:
        gid = r["source_group_id"]
        group_map.setdefault(gid, []).append(r["support_level"].lower())

    # Count complete 3-tier groups (Mild, Moderate, Strong)
    complete_groups = [gid for gid, tiers in group_map.items() if {"mild", "moderate", "strong"}.issubset(set(tiers))]
    assert len(complete_groups) == 70
    assert len(complete_groups) * 3 == 210
