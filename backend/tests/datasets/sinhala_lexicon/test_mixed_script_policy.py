"""
Tests for Mixed-Script Policy in Stage 32.
Ensures tokens containing non-Sinhala code points route strictly to manual review or exclusion.
"""

import pytest
from app.datasets.sinhala_lexicon.quality_router import LexiconQualityRouter

def test_mixed_script_latin_sinhala():
    router = LexiconQualityRouter()
    flags, findings, _, _ = router.screen_surface_form("bookඑක")
    assert "MIXED_SCRIPT_PRESENT" in flags
    assert any(f.reason_code == "MIXED_SCRIPT_PRESENT" for f in findings)

def test_pure_sinhala_word_has_no_mixed_script_flag():
    router = LexiconQualityRouter()
    flags, findings, _, _ = router.screen_surface_form("පොත")
    assert "MIXED_SCRIPT_PRESENT" not in flags
    assert len(findings) == 0
