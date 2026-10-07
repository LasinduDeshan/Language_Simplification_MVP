"""
Unit tests for Stage 20 Leakage Detector.
"""
import pytest
from app.datasets.expansion.leakage_detector import LeakageDetector

def test_split_containment_clean():
    detector = LeakageDetector(adaptation_test_ids={"C3-ADAPT-01"})
    splits = {
        "development_candidate_train": [
            {"source_item_id": "SRC-1", "pair_id": "SIMP-1"},
            {"source_item_id": "SRC-1", "pair_id": "SIMP-2"}
        ],
        "development_candidate_validation": [
            {"source_item_id": "SRC-2", "pair_id": "SIMP-3"}
        ],
        "development_candidate_test": [
            {"source_item_id": "SRC-3", "pair_id": "SIMP-4"}
        ]
    }
    res = detector.check_split_containment(splits)
    assert res["is_clean"] is True
    assert res["status"] == "passed"

def test_split_containment_leakage_detected():
    detector = LeakageDetector()
    splits = {
        "development_candidate_train": [
            {"source_item_id": "SRC-1", "pair_id": "SIMP-1"}
        ],
        "development_candidate_test": [
            {"source_item_id": "SRC-1", "pair_id": "SIMP-2"}  # Leaked!
        ]
    }
    res = detector.check_split_containment(splits)
    assert res["is_clean"] is False
    assert len(res["group_leakage_violations"]) == 1

def test_adaptation_test_isolation_violation():
    detector = LeakageDetector(adaptation_test_ids={"C3-ADAPT-01"})
    splits = {
        "development_candidate_train": [
            {"activity_id": "C3-ADAPT-01", "pair_id": "SIMP-1"}
        ]
    }
    res = detector.check_split_containment(splits)
    assert res["is_clean"] is False
    assert len(res["adaptation_test_leakage"]) == 1
