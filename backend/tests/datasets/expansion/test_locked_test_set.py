"""
Unit tests for Stage 20 Locked Test Manifest.
"""
import pytest
import os
import tempfile
import json
from app.datasets.expansion.split_builder import SplitBuilder

def test_locked_test_manifest_content():
    splitter = SplitBuilder(seed=42)
    test_recs = [
        {"pair_id": "SIMP-1", "source_item_id": "SRC-1", "original_text": "Secret test sentence", "simplified_text": "Secret simplified"}
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, "locked_test_manifest.json")
        manifest = splitter.generate_locked_test_manifest(test_recs, out_path, dataset_version="0.2.0")
        
        assert manifest["manifest_type"] == "locked_test_manifest"
        assert manifest["total_test_records"] == 1
        
        # Ensure raw sentence text is NOT stored in manifest
        entry = manifest["records"][0]
        assert "original_text" not in entry
        assert "simplified_text" not in entry
        assert "content_hash_sha256" in entry
        assert entry["record_id"] == "SIMP-1"
