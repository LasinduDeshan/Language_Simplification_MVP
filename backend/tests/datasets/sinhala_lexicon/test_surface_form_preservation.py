"""
Tests for Surface Form Preservation and Mapping Integrity in Stage 32 (WP4).
Ensures empirical surface tokens are never overwritten by lemmatization.
"""

from pathlib import Path
import pytest

from app.datasets.sinhala_lexicon.morphology_analyzer import MorphologyAnalyzer
from app.datasets.sinhala_lexicon.surface_form_grouper import SurfaceFormGrouper
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry, RightsProfileReference
from app.datasets.sinhala_lexicon.enums import LemmaMethod

def test_surface_form_never_overwritten_by_lemma():
    """Verify surface form remains preserved in candidate entry even when lemma differs."""
    entry = CandidateLexiconEntry(
        entry_id="SI-LEX-000001",
        canonical_form="ගස්වල",
        grapheme_count=4,
        code_point_count=6,
        canonical_frequency=5,
        canonical_document_frequency=3,
        weighted_provenance_frequency=5.0,
        source_count=2,
        eligible_source_count=5,
        observed_source_count=2,
        source_dispersion=0.50,
        rights_profile_refs=[
            RightsProfileReference(source_id="SRC-SI-001", rights_profile_id="RP-1", rights_profile_version=1)
        ]
    )

    grouper = SurfaceFormGrouper()
    updated, mappings = grouper.apply_morphology_and_build_mappings([entry])

    res = updated[0]
    # Surface form is intact
    assert res.canonical_form == "ගස්වල"
    # Candidate lemma is hypothesized
    assert res.candidate_lemma != ""
    assert res.lemma_method == LemmaMethod.RULE_BASED_INFLECTION_V1
    assert res.lemma_confidence > 0.0
