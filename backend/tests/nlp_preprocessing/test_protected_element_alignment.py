"""
Unit tests for Protected Element Alignment
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer
from app.nlp_preprocessing.protected_elements import ProtectedElementExtractor

def test_protected_element_alignment_success():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Pour the warm water into the glass cup carefully."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "PROT-ALIGN-01")
    
    protected_units = ["warm water", "glass cup", "pour"]
    feats = extractor.extract_features(sents, protected_units)
    
    aligned = feats.aligned_protected_units
    assert len(aligned) == 3
    for unit in aligned:
        assert unit["status"] == "aligned"
        assert unit["is_aligned"] is True

def test_protected_element_alignment_unaligned_warning():
    analyzer = LinguisticAnalyzer()
    extractor = ProtectedElementExtractor()
    text = "Put the pencil on the desk."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "PROT-ALIGN-02")
    
    protected_units = ["blue pencil", "desk"]
    feats = extractor.extract_features(sents, protected_units)
    
    aligned = {u["protected_unit"]: u for u in feats.aligned_protected_units}
    assert aligned["desk"]["status"] == "aligned"
    assert aligned["blue pencil"]["status"] == "unaligned_warning"
    assert aligned["blue pencil"]["is_aligned"] is False
