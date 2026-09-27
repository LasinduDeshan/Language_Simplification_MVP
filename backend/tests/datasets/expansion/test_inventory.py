"""
Unit tests for Stage 20 Dataset Inventory Analyzer.
"""
import pytest
from app.datasets.expansion.inventory import DatasetInventory

def test_inventory_analysis():
    inv = DatasetInventory()
    res = inv.analyze()
    
    assert res["baseline_release_version"] == "0.1.0"
    assert res["adaptation_test_set"]["total_records"] == 40
    assert res["simplification_corpus"]["total_pairs"] == 210
    assert res["lexicon_repository"]["total_entries"] == 18
    
    # Check domain distributions
    assert "vocabulary" in res["simplification_corpus"]["domain_distribution"]
    assert "easy" in res["adaptation_test_set"]["difficulty_distribution"]
    assert 4 in res["simplification_corpus"]["age_coverage"]

def test_inventory_markdown_generation():
    inv = DatasetInventory()
    md = inv.generate_markdown_report()
    assert "# Stage 20: Internal English Dataset Inventory Report" in md
    assert "40 activities" in md
    assert "210 draft pairs" in md
    assert "18 entries" in md
