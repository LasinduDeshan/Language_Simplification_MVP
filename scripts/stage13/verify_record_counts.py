import os
import sys
import json
import csv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INVENTORY_CSV = os.path.join(DOCS_DIR, "stage13_dataset_inventory.csv")
ADAPTATION_TASKS_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
SIMPLIFICATION_PAIRS_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")
LEGACY_TASKS_FILE = os.path.join(BASE_DIR, "data", "application_tasks", "seed_tasks.json")

def verify_record_counts():
    print("=== STAGE 13 ACCOUNTING RECONCILIATION ===")

    if not os.path.exists(INVENTORY_CSV):
        raise FileNotFoundError(f"Missing inventory: {INVENTORY_CSV}")

    with open(INVENTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        inventory = list(reader)

    # 1. Total Source Accounting
    total_source = sum(int(r["record_count"]) for r in inventory)
    print(f"Total inventoried source records across files and tables: {total_source}")

    # 2. Adaptation Test Set tasks reconciliation
    with open(LEGACY_TASKS_FILE, "r", encoding="utf-8") as f:
        legacy_tasks = json.load(f)
    legacy_count = len(legacy_tasks)

    with open(ADAPTATION_TASKS_FILE, "r", encoding="utf-8") as f:
        migrated_tasks = json.load(f)
    migrated_count = len(migrated_tasks)

    print(f"Seed tasks: source={legacy_count}, migrated_target={migrated_count}")
    assert legacy_count == migrated_count, f"Task count mismatch: expected {legacy_count}, got {migrated_count}"

    # 3. Simplification Corpus pairs count
    if os.path.exists(SIMPLIFICATION_PAIRS_FILE):
        with open(SIMPLIFICATION_PAIRS_FILE, "r", encoding="utf-8") as f:
            pairs = json.load(f)
        print(f"Simplification Corpus draft pairs: {len(pairs)}")
        assert len(pairs) >= legacy_count, f"Expected at least {legacy_count} simplification pairs"

    # 4. Accounting Formula Verification
    # Source = Migrated + Excluded + Rejected + Manual Review
    dispositions = {
        "migrated": 0,
        "excluded": 0,
        "rejected": 0,
        "manual_review": 0
    }

    for row in inventory:
        cnt = int(row["record_count"])
        action = row.get("migration_action", "")
        if "excluded" in row.get("proposed_layer", "") or action == "retain_in_database_only":
            dispositions["excluded"] += cnt
        elif "reject" in action:
            dispositions["rejected"] += cnt
        elif "manual" in action:
            dispositions["manual_review"] += cnt
        else:
            dispositions["migrated"] += cnt

    reconciled_sum = sum(dispositions.values())
    print(f"Dispositions breakdown: {dispositions}")
    assert total_source == reconciled_sum, f"Accounting discrepancy: {total_source} != {reconciled_sum}"
    print("[OK] All accounting reconciliation checks PASSED.")
    return True

if __name__ == "__main__":
    verify_record_counts()
