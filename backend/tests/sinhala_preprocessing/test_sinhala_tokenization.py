"""
Tests for Stage 30 Grapheme-Safe Tokenization.
"""

from app.sinhala_preprocessing.tokenizer import tokenize_text
from app.sinhala_preprocessing.schemas import TokenType

def test_token_classification():
    text = "Grade 2 සිසුන් 10ක් පොත් කියවයි."
    tokens = tokenize_text(text)

    types = [t.token_type for t in tokens]
    assert TokenType.LATIN_WORD in types
    assert TokenType.ARABIC_NUMBER in types
    assert TokenType.SINHALA_WORD in types
    assert TokenType.PUNCTUATION in types

def test_mixed_script_token():
    text = "1වන පාඩම"
    tokens = tokenize_text(text)
    assert tokens[0].token_type == TokenType.MIXED_SCRIPT_TOKEN

def test_lith_digit_token():
    text = "අංකය ෧ වේ."
    tokens = tokenize_text(text)
    assert any(t.token_type == TokenType.SINHALA_NUMBER for t in tokens)

def test_lossless_token_reconstruction():
    text = "මම පාසල් යමි. ගුරුවරයා උගන්වයි."
    tokens = tokenize_text(text)

    # 1. Exact slice verification per token
    for t in tokens:
        extracted = text[t.start_code_point:t.end_code_point]
        assert extracted == t.surface, f"Token slice mismatch for {t.surface}"

    # 2. Exact normalized-text reconstruction: NormalizedText = G_0 + sum(T_i + G_{i+1})
    # G_0 = text[:token_0.start]
    # T_i = text[token_i.start:token_i.end]
    # G_{i+1} = text[token_i.end:token_{i+1}.start]
    # G_N = text[token_{N-1}.end:]
    reconstructed_parts: list[str] = []
    last_idx = 0
    for t in tokens:
        # Appends G_i (where G_0 is initial gap)
        reconstructed_parts.append(text[last_idx:t.start_code_point])
        # Appends T_i
        reconstructed_parts.append(t.surface)
        last_idx = t.end_code_point
    # Appends final gap G_N
    reconstructed_parts.append(text[last_idx:])
    reconstructed_text = "".join(reconstructed_parts)
    assert reconstructed_text == text, "Exact normalized-text reconstruction failed"

def test_grapheme_integrity_in_tokens():
    text = "ශ්‍රී ලංකාව"
    tokens = tokenize_text(text)
    assert len(tokens) == 2
    assert tokens[0].surface == "ශ්‍රී"
    assert tokens[0].grapheme_count == 2
    assert tokens[1].surface == "ලංකාව"
    assert tokens[1].grapheme_count == 3
