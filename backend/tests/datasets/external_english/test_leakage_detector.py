"""Unit tests for external dataset leakage detection."""

import pytest
from app.datasets.external_english.adapters.asset_adapter import ASSETAdapter
from app.datasets.external_english.leakage import ExternalLeakageDetector


def test_leakage_detector_on_asset():
    adapter = ASSETAdapter()
    records = adapter.load_test_records()[:50]  # sample of 50 for quick test
    
    detector = ExternalLeakageDetector()
    report = detector.check_leakage(records)
    
    assert report["total_source_groups_checked"] == 50
    assert report["total_reference_instances_checked"] == 500
    assert report["leakage_status"] == "CLEAN"
    assert report["exact_overlap_count"] == 0
    assert report["enforced_governance_posture"]["evaluation_protected"] is True
    assert report["enforced_governance_posture"]["training_eligible"] is False
