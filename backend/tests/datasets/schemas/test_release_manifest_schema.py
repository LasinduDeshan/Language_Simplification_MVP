import pytest
from app.datasets.common.release_manifest import (
    ReleaseManifestV1, ReleaseFileEntryV1, RecordCountSummaryV1
)

def test_release_manifest_valid():
    counts = RecordCountSummaryV1(
        adaptation_activities=40,
        simplification_pairs=210,
        lexicon_entries=18,
        total_reusable_records=268
    )
    
    file_entry = ReleaseFileEntryV1(
        path="data/adaptation_test_set/releases/0.1.0/adaptation_test_set.json",
        size_bytes=12345,
        sha256="a" * 64,
        record_count=40
    )

    manifest = ReleaseManifestV1(
        manifest_id="MANIFEST-0.1.0",
        dataset_name="Language_Simplification_MVP_Datasets",
        dataset_version="0.1.0",
        schema_version="1.0.0",
        release_status="draft",
        record_counts=counts,
        files=[file_entry]
    )
    assert manifest.manifest_id == "MANIFEST-0.1.0"
    assert manifest.record_counts.total_reusable_records == 268

def test_release_manifest_invalid_counts_raises():
    counts = RecordCountSummaryV1(
        adaptation_activities=40,
        simplification_pairs=210,
        lexicon_entries=18,
        total_reusable_records=300  # Incorrect sum
    )
    
    with pytest.raises(ValueError, match="total_reusable_records"):
        ReleaseManifestV1(
            manifest_id="MANIFEST-0.1.0",
            dataset_name="Language_Simplification_MVP_Datasets",
            record_counts=counts
        )

def test_release_file_entry_sha256_length():
    with pytest.raises(Exception):
        ReleaseFileEntryV1(
            path="data/test.json",
            size_bytes=100,
            sha256="short_hash"  # Not 64 chars
        )
