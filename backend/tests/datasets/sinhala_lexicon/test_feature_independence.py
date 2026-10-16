"""
Tests for Feature Independence in Stage 32 Lexicon Construction (WP6).
Verifies that structural, frequency, and dispersion dimensions are preserved
without ad-hoc composite collapse.
"""

from pathlib import Path
import pytest

from app.datasets.sinhala_lexicon.feature_builder import LexiconFeatureBuilder

def test_feature_independence_dimensions():
    """Verify byte, code point, grapheme, consonant, and dispersion dimensions remain distinct."""
    fb = LexiconFeatureBuilder()
    surface = "ශ්‍රීලංකා"
    feats = fb.build_entry_features(
        surface=surface,
        canonical_freq=10,
        canonical_doc_freq=6,
        source_freq_dist={"SRC-1": 6, "SRC-2": 4},
        eligible_source_count=5
    )

    # Distinct physical and unicode length dimensions
    assert feats["utf8_byte_count"] > feats["code_point_count"]
    assert feats["code_point_count"] > feats["grapheme_count"]
    assert feats["has_joiner"] is True
    assert feats["syllable_proxy_count"] >= 1
    assert 0.0 < feats["source_dispersion"] <= 1.0
