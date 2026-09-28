"""
Unit tests for Deterministic Fallback Pipeline
"""
from app.nlp_preprocessing.fallback import DeterministicFallbackPipeline

def test_fallback_pipeline_basic_processing():
    fallback = DeterministicFallbackPipeline()
    text = "Look at the bright star. It shines in the night sky."
    offset_map = list(range(len(text)))
    
    sents, feats = fallback.process(text, offset_map, "FB-01")
    
    assert len(sents) == 2
    assert sents[0].text == "Look at the bright star."
    assert sents[1].text == "It shines in the night sky."
    
    assert feats is not None
    assert feats.surface.sentence_count == 2
    assert feats.surface.word_count > 0
    assert feats.surface.token_count > 0
    assert feats.syntactic.fragment_detected is True  # fallback defaults to degraded mode

def test_fallback_syllable_counter():
    fallback = DeterministicFallbackPipeline()
    assert fallback.count_syllables("cat") == 1
    assert fallback.count_syllables("water") == 2
    assert fallback.count_syllables("elephant") == 3
    assert fallback.count_syllables("") == 1
