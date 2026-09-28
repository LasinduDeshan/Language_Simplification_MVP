"""
Unit tests for Number & Quantity Extraction
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.protected_elements import ProtectedElementExtractor

def test_number_and_quantity_extraction():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Leo planted 4 seeds and found three coins."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    
    feats = extractor.extract_features(sents, [])
    assert "4" in feats.quantity_numbers
    assert "three" in feats.quantity_numbers
