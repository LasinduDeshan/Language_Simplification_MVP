"""
Unit tests for Cache Key Generation and Multi-Tier Invalidation
"""
from app.nlp_preprocessing.cache import PreprocessingCache

def test_cache_key_generation_and_invalidation():
    cache = PreprocessingCache(enabled=True)
    
    key1 = cache.get_processing_cache_key(
        normalized_text="hello world",
        language="en",
        pipeline_version="1.0.0",
        config_hash="conf_hash_1",
        model_hash="model_hash_1",
        lexicon_version="lex_v1"
    )
    
    # Same inputs -> same key
    key2 = cache.get_processing_cache_key(
        normalized_text="hello world",
        language="en",
        pipeline_version="1.0.0",
        config_hash="conf_hash_1",
        model_hash="model_hash_1",
        lexicon_version="lex_v1"
    )
    assert key1 == key2
    
    # Changed text -> different key
    key_diff_text = cache.get_processing_cache_key(
        normalized_text="hello world!",
        language="en",
        pipeline_version="1.0.0",
        config_hash="conf_hash_1",
        model_hash="model_hash_1",
        lexicon_version="lex_v1"
    )
    assert key1 != key_diff_text
    
    # Changed pipeline version -> different key
    key_diff_ver = cache.get_processing_cache_key(
        normalized_text="hello world",
        language="en",
        pipeline_version="1.0.1",
        config_hash="conf_hash_1",
        model_hash="model_hash_1",
        lexicon_version="lex_v1"
    )
    assert key1 != key_diff_ver
