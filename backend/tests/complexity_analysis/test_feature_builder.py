"""Unit tests for FeatureBuilder feature extraction and standardization."""

import numpy as np
from app.complexity_analysis.feature_builder import FeatureBuilder


def test_feature_builder_extraction():
    builder = FeatureBuilder()
    raw_record = {
        "char_count": 50,
        "token_count": 10,
        "word_count": 10,
        "sentence_count": 1,
        "punct_count": 1,
        "avg_word_length": 5.0,
        "avg_sentence_length": 10.0,
        "syllable_count": 15,
        "long_word_count": 2,
        "type_token_ratio": 0.9,
        "noun_count": 3,
        "verb_count": 2,
        "adj_count": 1,
        "adv_count": 1,
        "max_dependency_depth": 3,
        "avg_dependency_depth": 1.5,
        "clause_count": 1,
        "passive_voice": True,
        "negation_count": 0,
        "quantity_count": 1,
    }
    extracted = builder.extract_raw_features(raw_record)
    assert extracted["word_count"] == 10.0
    assert extracted["passive_voice"] == 1.0
    assert extracted["content_word_ratio"] == 0.7  # (3+2+1+1)/10


def test_feature_builder_fit_transform():
    records = [
        {"char_count": 20, "word_count": 5, "sentence_count": 1, "token_count": 5, "passive_voice": False},
        {"char_count": 40, "word_count": 10, "sentence_count": 1, "token_count": 10, "passive_voice": True},
        {"char_count": 60, "word_count": 15, "sentence_count": 2, "token_count": 15, "passive_voice": False},
    ]
    builder = FeatureBuilder()
    X = builder.fit_transform(records)
    assert X.shape[0] == 3
    assert X.shape[1] == len(builder.feature_names)
    assert isinstance(X, np.ndarray)
