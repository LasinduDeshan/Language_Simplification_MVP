"""
Unit tests for Stage 20 Candidate Split Eligibility Check.
"""
import pytest
from app.datasets.expansion.split_builder import SplitBuilder

def test_split_eligibility_filter():
    splitter = SplitBuilder()
    
    valid_record = {
        "source_item_id": "SRC-1",
        "pair_id": "SIMP-1",
        "schema_version": "1.0.0",
        "quality_status": "automatic_check_passed",
        "provenance": {"created_by": "user", "batch_id": "B1", "rights_status": "internal_team_owned"}
    }
    
    invalid_record = {
        "source_item_id": "SRC-2",
        "pair_id": "SIMP-2",
        "schema_version": "1.0.0",
        "quality_status": "failed",
        "unresolved_review": True,
        "provenance": {"created_by": "user", "batch_id": "B1"}
    }

    eligible, excluded = splitter.filter_candidate_eligibility([valid_record, invalid_record])
    assert len(eligible) == 1
    assert len(excluded) == 1
    assert eligible[0]["pair_id"] == "SIMP-1"
    assert excluded[0]["record_id"] == "SIMP-2"
