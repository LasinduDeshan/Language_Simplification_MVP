"""
Unit tests for Dependency Parsing
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_dependency_parsing_structure():
    analyzer = LinguisticAnalyzer()
    text = "The cat slept on the mat."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    tokens = sents[0].tokens
    
    deps = {t.text: t.dependency for t in tokens}
    assert deps["slept"] == "ROOT"
    
    # Check head indices within bounds
    for t in tokens:
        assert 0 <= t.head_index < len(tokens)
