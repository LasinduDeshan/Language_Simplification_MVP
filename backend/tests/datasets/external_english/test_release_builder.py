"""Unit tests for non-reconstructable external release builder."""

import json
from pathlib import Path
import pytest
import tempfile

from app.datasets.external_english.adapters.asset_adapter import ASSETAdapter
from app.datasets.external_english.release import ExternalReleaseBuilder


def test_release_builder_non_reconstructability(tmp_path):
    adapter = ASSETAdapter()
    records = adapter.load_test_records()[:10]
    
    mock_eval = {"test": {"baselines": {}}}
    mock_leakage = {"exact_overlap_count": 0, "near_overlap_count": 0, "leakage_status": "CLEAN"}
    
    builder = ExternalReleaseBuilder(output_dir=tmp_path)
    res = builder.build_release(records, mock_eval, mock_leakage)
    
    # Check that release files were created
    meta_file = tmp_path / "record_metadata.jsonl"
    assert meta_file.exists()
    
    manifest_file = tmp_path / "release_manifest.sha256"
    assert manifest_file.exists()
    
    # Verify non-reconstructability: raw sentences, references, or n-grams MUST NOT be in metadata
    with open(meta_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    
    assert len(lines) == 10
    for entry in lines:
        assert "raw_source_text" not in entry
        assert "raw_references" not in entry
        assert "evaluation_source_text" not in entry
        assert "evaluation_references" not in entry
        assert "tokens" not in entry
        assert "n_grams" not in entry
        assert "numerical_features" in entry
        assert "content_hash" in entry
        assert entry["evaluation_protected"] is True
