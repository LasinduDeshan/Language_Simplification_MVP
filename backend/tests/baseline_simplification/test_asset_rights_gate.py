"""
Unit tests for ASSET rights boundary and non-redistribution governance.
"""
from pathlib import Path
from app.baseline_simplification.runner import BaselineRunner
from app.baseline_simplification.schemas import BaselineMethodId, ProtectedElementSource

def test_asset_records_governance_posture():
    runner = BaselineRunner()
    sample_asset = [
        {"source_item_id": "ASSET-TEST-SRC-0001", "source_text": "He lived in an old cottage.", "target_content_age": 6}
    ]
    records = runner.run_on_items(
        BaselineMethodId.B0,
        sample_asset,
        dataset_id="asset",
        dataset_version="0.1.0",
        split="test",
        run_id="TEST-ASSET",
        validation_mode=ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY,
    )
    assert len(records) == 1
    r = records[0]
    assert r.approved_for_child_delivery is False
    assert r.requires_expert_review is True
    assert r.validation_status == "draft"
    assert r.research_eligible is False
