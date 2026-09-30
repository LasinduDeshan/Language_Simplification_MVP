"""
Unit tests for locked test split isolation and non-contamination guarantees.
"""
from pathlib import Path
import json

def test_locked_test_split_isolation():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    locked_manifest = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "splits" / "locked_test_manifest.json"
    assert locked_manifest.exists()
    
    with open(locked_manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    records = manifest.get("records", [])
    assert len(records) == 135
    unique_groups = set(r["source_group_id"] for r in records)
    assert len(unique_groups) == 45

    # Check results file
    test_results_file = repo_root / "data" / "baseline_simplification" / "results" / "internal" / "internal_locked_test_summary.json"
    if test_results_file.exists():
        with open(test_results_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
        for m, s in summary.items():
            assert s["total_records"] == 45
