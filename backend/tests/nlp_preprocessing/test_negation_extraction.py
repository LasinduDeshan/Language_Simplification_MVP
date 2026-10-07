"""
Unit tests for Negation Extraction
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.protected_elements import ProtectedElementExtractor

def test_negation_extraction_explicit_and_conditional():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Do not touch the red box; otherwise, pick the blue circle."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    
    feats = extractor.extract_features(sents, [])
    assert "not" in feats.negation_markers
    assert "otherwise" in feats.negation_markers
