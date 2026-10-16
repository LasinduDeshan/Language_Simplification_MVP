"""
Tests for Proper Noun Policy and Named Entity Routing in Stage 32.
"""

import pytest
from app.datasets.sinhala_lexicon.quality_router import LexiconQualityRouter

def test_proper_noun_marker_handling():
    router = LexiconQualityRouter()
    # Clean standard lexical words do not trigger proper noun flags
    flags, findings, is_proper, is_sensitive = router.screen_surface_form("ගස")
    assert not is_proper
    assert len(flags) == 0

def test_extreme_token_length_flag():
    router = LexiconQualityRouter()
    long_compound = "ශ්‍රීලංකාප්‍රජාතාන්ත්‍රිකසමාජවාදීජනරජය"
    flags, findings, _, _ = router.screen_surface_form(long_compound)
    assert "COMPLEX_OR_RARE_FORM_REVIEW" in flags
    assert any(f.reason_code == "COMPLEX_OR_RARE_FORM_REVIEW" for f in findings)
