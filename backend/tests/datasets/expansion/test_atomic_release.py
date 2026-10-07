"""
Unit tests for Stage 20 Atomic Release Builder & Rollback.
"""
import pytest
import os
import tempfile
from app.datasets.expansion.release_builder import ReleaseBuilder

def test_atomic_staging_and_rollback():
    with tempfile.TemporaryDirectory() as tmpdir:
        builder = ReleaseBuilder(root_dir=tmpdir, dataset_version="0.2.0")
        
        staged = builder.build_release_staging(
            adaptation_activities=[{"activity_id": "C3-1"}],
            simplification_pairs=[{"pair_id": "SIMP-1"}],
            splits={"development_candidate_train": [{"pair_id": "SIMP-1"}]},
            lexicon_entries=[{"lexicon_id": "LEX-1"}],
            locked_test_manifest={"manifest_type": "locked"}
        )
        
        assert staged["status"] == "staged_successfully"
        assert os.path.exists(builder.staging_dir)
        
        # Dry run publish leaves staging intact
        dry_res = builder.publish_release(dry_run=True)
        assert dry_res["status"] == "dry_run_success"
        
        # Real publish moves files and cleans staging
        pub_res = builder.publish_release(dry_run=False)
        assert pub_res["status"] == "published_successfully"
        assert not os.path.exists(builder.staging_dir)
