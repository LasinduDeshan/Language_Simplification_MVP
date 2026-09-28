"""
Unit tests for text deduplication by text_hash
"""
from app.nlp_preprocessing.cache import PreprocessingCache
from app.nlp_preprocessing.schemas import TextInstance

def test_text_hash_deduplication():
    cache = PreprocessingCache(enabled=False)
    t1 = "Put the red ball in the box."
    t2 = "Put the red ball in the box."
    t3 = "Put the blue ball in the box."
    
    h1 = cache.get_text_hash(t1)
    h2 = cache.get_text_hash(t2)
    h3 = cache.get_text_hash(t3)
    
    assert h1 == h2
    assert h1 != h3
