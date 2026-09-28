"""
Unit tests for Tokenization
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_tokenization_properties():
    analyzer = LinguisticAnalyzer()
    text = "Find 4 red apples!"
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    tokens = sents[0].tokens
    
    token_texts = [t.text for t in tokens]
    assert "Find" in token_texts
    assert "4" in token_texts
    assert "apples" in token_texts
    assert "!" in token_texts
    
    num_tok = [t for t in tokens if t.text == "4"][0]
    assert num_tok.is_num is True
    
    punct_tok = [t for t in tokens if t.text == "!"][0]
    assert punct_tok.is_punct is True
