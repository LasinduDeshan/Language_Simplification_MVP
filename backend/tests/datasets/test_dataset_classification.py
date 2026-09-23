import os
import csv
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
INVENTORY_CSV = os.path.join(BASE_DIR, "docs", "stage13_dataset_inventory.csv")

def test_inventory_file_exists():
    assert os.path.exists(INVENTORY_CSV), "stage13_dataset_inventory.csv must exist in docs/"

def test_all_sources_have_valid_classification():
    with open(INVENTORY_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    assert len(rows) >= 19, f"Expected at least 19 inventoried sources, found {len(rows)}"
    
    for r in rows:
        layer = r["proposed_layer"]
        assert any(layer.startswith(prefix) for prefix in [
            "adaptation_test_set",
            "simplification_corpus",
            "interaction_dataset",
            "lexicons",
            "excluded_from_reusable_datasets"
        ]), f"Invalid proposed layer: {layer}"
        assert int(r["record_count"]) >= 0, f"Record count must be non-negative: {r['record_count']}"
        assert r["data_owner"] in {"component_1", "component_2_ar", "component_3"}
