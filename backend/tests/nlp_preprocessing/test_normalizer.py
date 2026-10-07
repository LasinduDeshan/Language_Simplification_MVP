"""
Unit tests for Unicode Normalizer
"""
from app.nlp_preprocessing.normalizer import UnicodeNormalizer

def test_nfc_normalization_determinism():
    normalizer = UnicodeNormalizer(form="NFC")
    text_with_curly_quotes = "Let’s read the “story”."
    norm, offset_map = normalizer.normalize(text_with_curly_quotes)
    
    assert norm == "Let's read the \"story\"."
    assert len(offset_map) == len(norm)
    assert offset_map[0] == 0
