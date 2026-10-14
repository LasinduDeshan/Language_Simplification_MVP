"""
Feature extraction module for Stage 30 Sinhala Preprocessing.
Extracts purely deterministic, technical, and structural features.
Explicitly non-authoritative: does NOT compute reading age, readability, or clinical scores.
"""

from typing import List
from app.sinhala_preprocessing.schemas import (
    OperationRecord,
    PreprocessingFeatures,
    SentenceRecord,
    TokenRecord,
    TokenType
)
from app.sinhala_preprocessing.graphemes import count_graphemes

def build_preprocessing_features(
    raw_text: str,
    normalized_text: str,
    sentences: List[SentenceRecord],
    tokens: List[TokenRecord],
    operations: List[OperationRecord]
) -> PreprocessingFeatures:
    raw_bytes = len(raw_text.encode("utf-8"))
    raw_cps = len(raw_text)
    raw_graphemes = count_graphemes(raw_text)

    norm_bytes = len(normalized_text.encode("utf-8"))
    norm_cps = len(normalized_text)
    norm_graphemes = count_graphemes(normalized_text)

    s_count = len(sentences)
    t_count = len(tokens)

    sinhala_tokens = 0
    latin_tokens = 0
    mixed_tokens = 0
    numeric_tokens = 0
    punct_tokens = 0
    max_token_grapheme = 0
    total_token_graphemes = 0

    for t in tokens:
        g_len = t.grapheme_count
        total_token_graphemes += g_len
        if g_len > max_token_grapheme:
            max_token_grapheme = g_len

        if t.token_type == TokenType.SINHALA_WORD:
            sinhala_tokens += 1
        elif t.token_type == TokenType.LATIN_WORD:
            latin_tokens += 1
        elif t.token_type == TokenType.MIXED_SCRIPT_TOKEN:
            mixed_tokens += 1
        elif t.token_type in (TokenType.ARABIC_NUMBER, TokenType.SINHALA_NUMBER):
            numeric_tokens += 1
        elif t.token_type == TokenType.PUNCTUATION:
            punct_tokens += 1

    mean_g_per_t = round(total_token_graphemes / t_count, 4) if t_count > 0 else 0.0
    mean_t_per_s = round(t_count / s_count, 4) if s_count > 0 else 0.0

    nfc_ops = sum(1 for op in operations if op.operation_type == "UNICODE_NFC")
    ws_ops = sum(1 for op in operations if op.operation_type == "WHITESPACE_NORMALIZATION")

    return PreprocessingFeatures(
        raw_utf8_byte_count=raw_bytes,
        raw_code_point_count=raw_cps,
        raw_grapheme_count=raw_graphemes,
        normalized_utf8_byte_count=norm_bytes,
        normalized_code_point_count=norm_cps,
        normalized_grapheme_count=norm_graphemes,
        sentence_count=s_count,
        token_count=t_count,
        sinhala_token_count=sinhala_tokens,
        latin_token_count=latin_tokens,
        mixed_script_token_count=mixed_tokens,
        numeric_token_count=numeric_tokens,
        punctuation_token_count=punct_tokens,
        mean_graphemes_per_token=mean_g_per_t,
        mean_tokens_per_sentence=mean_t_per_s,
        max_token_grapheme_length=max_token_grapheme,
        normalization_operation_count=nfc_ops,
        whitespace_operation_count=ws_ops
    )
