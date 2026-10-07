"""
Unit tests for Sentence Segmentation
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_multistep_sentence_segmentation():
    analyzer = LinguisticAnalyzer()
    text = "1. Pick up the red ball. 2. Put it in the box."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    
    assert len(sents) >= 2
    assert "Pick up the red ball." in sents[0].text
    assert sents[0].tokens[0].text in ["1", "1."] or sents[0].tokens[0].text == "1"
