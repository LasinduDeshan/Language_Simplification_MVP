"""
Stage 20 Script: Verify Split Leakage
Validates group-aware split containment and Adaptation Test Set isolation, writing docs/stage20_leakage_report.csv.
"""
import os
import sys
import json
import csv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.leakage_detector import LeakageDetector
from app.datasets.expansion.split_builder import SplitBuilder

def main():
    print("=" * 60)
    print("STAGE 20: Verifying Group-Aware Split Containment & Anti-Leakage")
    print("=" * 60)
    
    # 1. Load Adaptation Test Set IDs
    adapt_path = os.path.join(ROOT_DIR, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
    with open(adapt_path, "r", encoding="utf-8") as f:
        adapt_data = json.load(f)
    adapt_ids = {r.get("activity_id") for r in (adapt_data if isinstance(adapt_data, list) else adapt_data.get("records", []))}

    # 2. Load all authored simplification pairs
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    all_pairs = []
    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_pairs.extend(data.get("simplification_pairs", []))

    # 3. Build candidate splits
    splitter = SplitBuilder(seed=42)
    eligible_pairs, excluded = splitter.filter_candidate_eligibility(all_pairs)
    splits = splitter.build_group_aware_splits(eligible_pairs)

    # 4. Detect leakage
    detector = LeakageDetector(adaptation_test_ids=adapt_ids)
    res = detector.check_split_containment(splits)

    out_csv = os.path.join(ROOT_DIR, "docs", "stage20_leakage_report.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["check_name", "group_id", "details", "status"])
        writer.writerow(["group_aware_isolation", "ALL_SOURCE_GROUPS", f"Isolated {res['total_groups_isolated']} groups", "PASSED" if len(res['group_leakage_violations']) == 0 else "FAILED"])
        writer.writerow(["adaptation_test_isolation", "ADAPTATION_TEST_SET", f"40 protected test activities isolated from candidate train", "PASSED" if len(res['adaptation_test_leakage']) == 0 else "FAILED"])

        for v in res["group_leakage_violations"]:
            writer.writerow(["group_leakage_violation", v["group_id"], f"Split {v['primary_split']} vs {v['leaked_split']}", "LEAKAGE_DETECTED"])
        for a in res["adaptation_test_leakage"]:
            writer.writerow(["adaptation_leakage_violation", a["activity_id"], a["reason"], "LEAKAGE_DETECTED"])

    print(f"Anti-leakage verification results:")
    print(f"  - Total source groups isolated:  {res['total_groups_isolated']}")
    print(f"  - Group cross-split violations: {len(res['group_leakage_violations'])}")
    print(f"  - Adaptation test leaks:         {len(res['adaptation_test_leakage'])}")
    print(f"  - Leakage Gate Status:           {'PASSED' if res['is_clean'] else 'FAILED'}")
    print(f"Report written to: {out_csv}")
    print("=" * 60)

if __name__ == "__main__":
    main()
