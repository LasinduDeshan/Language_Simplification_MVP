"""
Tests for Reused Governed Locked Benchmark Guard and Dual Reporting Manifest.
"""

import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent.parent


def test_locked_benchmark_manifest():
    manifest_file = repo_root / "data" / "model_simplification" / "manifests" / "stage26_locked_benchmark_manifest.json"
    assert manifest_file.exists(), "Locked benchmark manifest must exist."

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. Full reused locked benchmark (45 groups / 135 outputs)
    full_bench = manifest["full_reused_locked_benchmark"]
    assert full_bench["source_group_count"] == 45
    assert full_bench["pair_count"] == 135

    # 2. Predeclared clean text-simplification subset (13 groups / 39 outputs)
    clean_bench = manifest["predeclared_text_simplification_subset"]
    assert clean_bench["source_group_count"] == 13
    assert clean_bench["pair_count"] == 39


def test_locked_test_isolation():
    # Verify that locked test pairs are strictly excluded from the training eligibility manifest
    train_manifest_file = repo_root / "data" / "model_simplification" / "manifests" / "stage26_training_eligibility_manifest.json"
    with open(train_manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    for r in manifest["records"]:
        if r["split"] == "test":
            assert r["primary_eligibility_disposition"] in ["task_reformulation_excluded", "non_development_split_excluded"]
            assert r["internal_training_decision"] == "excluded_from_training"
