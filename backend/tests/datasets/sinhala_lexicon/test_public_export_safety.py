"""
Tests for Public Export Safety, Zero Context Leakage, and Keyed HMAC Verification (WP7).
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.export_service import LexiconExportService
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry, RightsProfileReference
from app.datasets.sinhala_lexicon.enums import FieldExportPolicy

def test_keyed_hmac_generation_with_domain_separation():
    """Verify runtime HMAC generation produces 64-char hex digest with domain separation."""
    svc = LexiconExportService()
    h1 = svc.compute_surface_hmac("SI-OCC-00000001", "අම්මා")
    h2 = svc.compute_surface_hmac("SI-OCC-00000002", "අම්මා")
    assert len(h1) == 64
    assert len(h2) == 64
    assert h1 != h2  # Different occurrence IDs yield distinct HMAC digests

def test_public_export_contains_zero_restricted_contexts(tmp_path):
    """Verify public metadata export contains zero context passages or unkeyed text hashes."""
    svc = LexiconExportService()
    svc.export_dir = tmp_path
    svc.public_export_file = tmp_path / "test_public_export.jsonl"

    entry = CandidateLexiconEntry(
        entry_id="SI-LEX-000001",
        canonical_form="ගස",
        grapheme_count=2,
        code_point_count=2,
        canonical_frequency=5,
        canonical_document_frequency=3,
        weighted_provenance_frequency=5.0,
        source_count=2,
        eligible_source_count=5,
        observed_source_count=2,
        source_dispersion=0.50,
        rights_profile_refs=[
            RightsProfileReference(source_id="SRC-1", rights_profile_id="RP-1", rights_profile_version=1)
        ]
    )

    out_file = svc.export_public_metadata([entry])
    assert out_file.exists()

    with open(out_file, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())

    # Verify approved fields present, restricted contexts absent
    assert data["entry_id"] == "SI-LEX-000001"
    assert data["canonical_form"] == "ගස"
    assert "concordance_contexts" not in data
    assert "context_storage_ref" not in data
    assert "raw_text_sha256" not in data
