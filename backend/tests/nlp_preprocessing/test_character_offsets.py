"""
Unit tests for Character Offset Mapping & Slice Integrity
"""
from app.nlp_preprocessing.normalizer import UnicodeNormalizer
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_character_offset_reconstruction_integrity():
    normalizer = UnicodeNormalizer()
    analyzer = LinguisticAnalyzer()
    
    raw_text = "The café serves delicious naïve pastries!"
    normalized_text, offset_map = normalizer.normalize(raw_text)
    
    sents = analyzer.analyze(normalized_text, raw_text, offset_map, "OFFSET-01")
    assert len(sents) == 1
    sent = sents[0]
    
    # Check sentence slice
    assert normalized_text[sent.normalized_start_char:sent.normalized_end_char] == sent.text
    assert raw_text[sent.original_start_char:sent.original_end_char] == sent.text
    
    # Check all token slices
    for tok in sent.tokens:
        norm_slice = normalized_text[tok.normalized_start_char:tok.normalized_end_char]
        orig_slice = raw_text[tok.original_start_char:tok.original_end_char]
        assert norm_slice == tok.text
        assert orig_slice == tok.text
