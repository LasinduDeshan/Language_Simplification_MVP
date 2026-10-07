"""
Unit tests for Lemmatization
"""
from app.nlp_preprocessing.linguistic_analyzer import LinguisticAnalyzer

def test_lemmatization_irregular_plurals_and_verbs():
    analyzer = LinguisticAnalyzer()
    text = "The children and mice ran quickly with their feet."
    offset_map = list(range(len(text)))
    sents = analyzer.analyze(text, text, offset_map, "TEST-01")
    tokens = sents[0].tokens
    
    lemmas = {t.text: t.lemma for t in tokens}
    assert lemmas["children"] == "child"
    assert lemmas["mice"] == "mouse"
    assert lemmas["ran"] == "run"
    assert lemmas["feet"] == "foot"
