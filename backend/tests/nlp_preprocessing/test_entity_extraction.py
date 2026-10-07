"""
Unit tests for Entity & Semantic Element Extraction
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.protected_elements import ProtectedElementExtractor

def test_entity_extraction_colors_and_proper_nouns():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Sara and Leo placed the yellow sunflower on the brown table."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "ENT-TEST-01")
    
    feats = extractor.extract_features(sents, [])
    entities = feats.named_entities
    
    # Check proper nouns
    propn_texts = [e["text"] for e in entities if e["category"] == "PERSON_OR_PLACE"]
    assert "Sara" in propn_texts or "Leo" in propn_texts
    
    # Check colors
    color_texts = [e["text"].lower() for e in entities if e["category"] == "COLOR"]
    assert "yellow" in color_texts
    assert "brown" in color_texts

def test_spatio_temporal_extraction():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Before eating, wash your hands under running water."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "ENT-TEST-02")
    
    feats = extractor.extract_features(sents, [])
    assert "before" in feats.temporal_connectives
    assert "under" in feats.spatial_prepositions
