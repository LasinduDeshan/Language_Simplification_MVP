"""
Unit tests for POS Tagging
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_pos_tagging_accuracy():
    analyzer = LinguisticAnalyzer()
    text = "She plays with a yellow ball."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    tokens = sents[0].tokens
    
    pos_map = {t.text: t.pos for t in tokens}
    assert pos_map["She"] == "PRON"
    assert pos_map["plays"] == "VERB"
    assert pos_map["yellow"] == "ADJ"
    assert pos_map["ball"] == "NOUN"
