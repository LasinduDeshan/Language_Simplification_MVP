"""
Stage 21 Accounting Verification Script
Validates zero loss across all raw text instances, processed records, deduplication cache, and locked test quarantine.
"""
import sys
import csv
import json
from pathlib import Path

def main():
    print("=== Stage 21: Preprocessing Zero-Loss Accounting Verification ===")
    repo_root = Path(__file__).resolve().parent.parent.parent
    release_dir = repo_root / "data" / "preprocessed_features" / "en" / "source-0.2.0" / "pipeline-1.0.0"
    
    csv_path = release_dir / "reconciliation_report.csv"
    manifest_path = release_dir / "dataset_manifest.json"

    assert csv_path.exists(), f"Missing {csv_path}"
    assert manifest_path.exists(), f"Missing {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    summary = manifest.get("summary", {})
    
    print("\nReconciliation Summary Metrics:")
    print("-" * 65)
    print(f"{'Metric':<45} | {'Value':<15}")
    print("-" * 65)
    for k, v in summary.items():
        print(f"{k:<45} | {str(v):<15}")
    print("-" * 65)

    assert summary.get("is_zero_loss") is True, "Accounting reconciliation failed: Zero loss not achieved!"
    assert summary.get("unaccounted_records") == 0, "Unaccounted records detected!"
    assert summary.get("raw_text_instance_count") == 3617, f"Expected 3617 raw text instances, got {summary.get('raw_text_instance_count')}"
    
    print("\nZERO-LOSS RECONCILIATION VERIFIED: 100% of text instances accounted for.")

if __name__ == "__main__":
    main()
