"""
Unit tests for Normalization Policy (NFKC restrictions and prohibited changes)
"""
import pytest
from app.nlp_preprocessing.normalizer import UnicodeNormalizer

def test_nfkc_disabled_by_default():
    with pytest.raises(ValueError):
        UnicodeNormalizer(form="NFKC", allow_nfkc_diagnostic=False)

def test_nfkc_enabled_with_diagnostic_flag():
    normalizer = UnicodeNormalizer(form="NFKC", allow_nfkc_diagnostic=True)
    norm, _ = normalizer.normalize("2² = 4")
    assert "22 = 4" in norm
