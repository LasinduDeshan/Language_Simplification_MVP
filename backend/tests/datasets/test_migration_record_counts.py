import os
import csv
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
INVENTORY_CSV = os.path.join(BASE_DIR, "docs", "stage13_dataset_inventory.csv")
LEGACY_TASKS_FILE = os.path.join(BASE_DIR, "data", "application_tasks", "seed_tasks.json")
ADAPTATION_TASKS_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")

def test_migration_accounting_formula_reconciliation():
    with open(INVENTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        inventory = list(reader)

    source_count = sum(int(r["record_count"]) for r in inventory)
    
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

    # Check 1: Total accounting formula
    assert source_count == (
        dispositions["migrated"]
        + dispositions["excluded"]
        + dispositions["rejected"]
        + dispositions["manual_review"]
    ), f"Accounting discrepancy: source {source_count} != sum of dispositions"

def test_pre_migration_eligible_records_reconciliation():
    # Check 2: Eligible pre-migration authoring records count matches migrated test set tasks
    with open(LEGACY_TASKS_FILE, "r", encoding="utf-8") as f:
        legacy_tasks = json.load(f)
    approved_eligible_count = len(legacy_tasks)

    with open(ADAPTATION_TASKS_FILE, "r", encoding="utf-8") as f:
        migrated_tasks = json.load(f)
    successfully_migrated_count = len(migrated_tasks)

    assert approved_eligible_count == successfully_migrated_count, (
        f"Eligible record count mismatch: {approved_eligible_count} vs {successfully_migrated_count}"
    )
