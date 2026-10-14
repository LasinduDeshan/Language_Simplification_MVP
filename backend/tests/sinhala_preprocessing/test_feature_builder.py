"""
Tests for Stage 30 Feature Extraction.
"""

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text

def test_preprocessing_features_structure():
    text = "Grade 1 සිසුන් 10ක් ඇත."
    rec = preprocess_sinhala_text(text)
    f = rec.features

    assert f.raw_utf8_byte_count > 0
    assert f.raw_code_point_count > 0
    assert f.raw_grapheme_count > 0
    assert f.sentence_count == 1
    assert f.token_count > 0
    assert f.sinhala_token_count > 0
    assert f.latin_token_count > 0
    assert f.numeric_token_count > 0
    assert f.mean_graphemes_per_token > 0
    assert f.mean_tokens_per_sentence > 0
    assert f.max_token_grapheme_length > 0
