import os
import sys
import json
import csv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INVENTORY_CSV = os.path.join(DOCS_DIR, "stage13_dataset_inventory.csv")

def classify_records():
    if not os.path.exists(INVENTORY_CSV):
        raise FileNotFoundError(f"Inventory not found at {INVENTORY_CSV}. Run inventory_existing_data.py first.")

    with open(INVENTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    classification_summary = {
        "adaptation_test_set": 0,
        "simplification_corpus": 0,
        "interaction_dataset": 0,
        "lexicons": 0,
        "excluded": 0,
        "total_source_records": 0
    }

    for row in rows:
        count = int(row["record_count"])
        classification_summary["total_source_records"] += count
        layer = row["proposed_layer"]
        if "adaptation_test_set" in layer:
            classification_summary["adaptation_test_set"] += count
        elif "simplification_corpus" in layer:
            classification_summary["simplification_corpus"] += count
        elif "interaction_dataset" in layer:
            classification_summary["interaction_dataset"] += count
        elif "lexicons" in layer:
            classification_summary["lexicons"] += count
        else:
            classification_summary["excluded"] += count

    print("=== STAGE 13 CLASSIFICATION SUMMARY ===")
    for k, v in classification_summary.items():
        print(f" - {k}: {v} records")

    return classification_summary

if __name__ == "__main__":
    classify_records()
