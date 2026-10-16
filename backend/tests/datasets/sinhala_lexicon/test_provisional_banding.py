"""
Tests for Provisional Vocabulary Banding Policy and Calibration Isolation in Stage 32 (WP6).
Verifies rule evidence generation, tie-breaking to review, and strict split group isolation.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.banding import ProvisionalBandingEngine
from app.datasets.sinhala_lexicon.enums import ProvisionalVocabularyBand, TerminalEntryDisposition
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry, RightsProfileReference

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

def test_provisional_banding_foundational_assignment():
    """Verify high frequency, high dispersion, short candidate receives FOUNDATIONAL_CANDIDATE."""
    engine = ProvisionalBandingEngine()
    entry = CandidateLexiconEntry(
        entry_id="SI-LEX-000001",
        canonical_form="අම්මා",
        grapheme_count=3,
        code_point_count=5,
        canonical_frequency=25,
        canonical_document_frequency=12,
        weighted_provenance_frequency=25.0,
        source_count=4,
        eligible_source_count=5,
        observed_source_count=4,
        source_dispersion=0.85,
        rights_profile_refs=[
            RightsProfileReference(source_id="SRC-1", rights_profile_id="RP-1", rights_profile_version=1)
        ]
    )

    band, conf, evidence = engine.assign_provisional_band(entry)
    assert band == ProvisionalVocabularyBand.FOUNDATIONAL_CANDIDATE
    assert conf >= 0.85
    assert "high_canonical_frequency" in evidence

def test_provisional_banding_tie_break_routes_to_review():
    """Verify candidates matching multiple conflicting thresholds route to REVIEW_REQUIRED."""
    engine = ProvisionalBandingEngine()
    # Construct an entry that matches both early and developing rule conditions if boundaries overlap
    entry = CandidateLexiconEntry(
        entry_id="SI-LEX-000002",
        canonical_form="පරීක්ෂණය",
        grapheme_count=6,
        code_point_count=9,
        canonical_frequency=1,  # Low frequency -> triggers advanced rule
        syllable_proxy_count=5,  # High syllable -> triggers advanced rule
        canonical_document_frequency=1,
        weighted_provenance_frequency=1.0,
        source_count=1,
        eligible_source_count=5,
        observed_source_count=1,
        source_dispersion=0.0,
        quality_flags=["SENSITIVE_VOCABULARY_FLAG"],
        terminal_entry_disposition=TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED,
        rights_profile_refs=[
            RightsProfileReference(source_id="SRC-1", rights_profile_id="RP-1", rights_profile_version=1)
        ]
    )

    band, conf, evidence = engine.assign_provisional_band(entry)
    assert band == ProvisionalVocabularyBand.REVIEW_REQUIRED

def test_calibration_isolation_blocks_eval_splits():
    """Verify that validation and locked_test split groups are forbidden from calibration."""
    engine = ProvisionalBandingEngine()
    forbidden = engine.config_data["calibration_protocol"]["forbidden_splits"]
    assert "validation" in forbidden
    assert "locked_test" in forbidden
