"""
Unit tests for Stage 20 Duplicate Detector.
"""
import pytest
from app.datasets.expansion.duplicate_detector import DuplicateDetector

def test_exact_duplicate_detection():
    detector = DuplicateDetector()
    records = [
        {"source_item_id": "SRC-1", "original_text": "Put the red ball in the box."},
        {"source_item_id": "SRC-2", "original_text": "Put the red ball in the box."}
    ]
    res = detector.scan_records(records)
    assert res["exact_duplicate_count"] == 1
    assert res["is_unique"] is False
    assert res["exact_duplicates"][0]["record_id"] == "SRC-2"

def test_near_duplicate_detection():
    detector = DuplicateDetector(jaccard_threshold=0.80)
    records = [
        {"source_item_id": "SRC-1", "original_text": "Put the bright red ball in the wooden box."},
        {"source_item_id": "SRC-2", "original_text": "Put the red ball in the wooden box."}
    ]
    res = detector.scan_records(records)
    assert res["near_duplicate_cluster_count"] >= 1
    assert res["near_duplicate_clusters"][0]["status"] == "manual_review_required"
