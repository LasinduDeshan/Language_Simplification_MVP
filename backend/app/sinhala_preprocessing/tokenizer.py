"""
Tokenization module for Stage 30 Sinhala Preprocessing.
Provides deterministic, grapheme-safe tokenization:
- Never splits an extended grapheme cluster.
- Classifies tokens into SINHALA_WORD, LATIN_WORD, MIXED_SCRIPT_TOKEN,
  ARABIC_NUMBER, SINHALA_NUMBER, PUNCTUATION, SYMBOL, UNKNOWN.
- Preserves code-point offsets [start, end) on normalized text.
- Supports lossless sentence reconstruction.
"""

import regex
import unicodedata
from typing import Dict, List, Tuple
from app.sinhala_preprocessing.schemas import TokenRecord, TokenType
from app.sinhala_preprocessing.graphemes import segment_graphemes, count_graphemes
from app.sinhala_preprocessing.script_analyzer import is_sinhala_cp, is_latin_cp, is_digit_cp

def classify_token_type(surface: str) -> Tuple[TokenType, Dict[str, float]]:
    sinhala = 0
    latin = 0
    arabic_num = 0
    sinhala_num = 0
    punct = 0
    symbol = 0
    other = 0

    total = len(surface)
    if total == 0:
        return TokenType.UNKNOWN, {}

    for char in surface:
        cp = ord(char)
        cat = unicodedata.category(char)

        if 0x0030 <= cp <= 0x0039:
            arabic_num += 1
        elif (0x0DE6 <= cp <= 0x0DEF) or (0x111E1 <= cp <= 0x111F4):
            sinhala_num += 1
        elif is_sinhala_cp(cp) or cp in (0x200D, 0x200C):
            sinhala += 1
        elif is_latin_cp(cp):
            latin += 1
        elif cat.startswith("P") or cp in (0x0DF4,):
            punct += 1
        elif cat.startswith("S"):
            symbol += 1
        else:
            other += 1

    profile = {
        "Sinh": round((sinhala + sinhala_num) / total, 4),
        "Latn": round(latin / total, 4),
        "Digit": round((arabic_num + sinhala_num) / total, 4)
    }

    if sinhala > 0 and latin > 0:
        return TokenType.MIXED_SCRIPT_TOKEN, profile
    elif sinhala > 0 and (sinhala + punct == total or sinhala == total):
        return TokenType.SINHALA_WORD, profile
    elif latin > 0 and (latin + punct == total or latin == total):
        return TokenType.LATIN_WORD, profile
    elif arabic_num == total:
        return TokenType.ARABIC_NUMBER, profile
    elif sinhala_num == total:
        return TokenType.SINHALA_NUMBER, profile
    elif punct == total:
        return TokenType.PUNCTUATION, profile
    elif symbol == total:
        return TokenType.SYMBOL, profile
    elif sinhala > 0:
        return TokenType.SINHALA_WORD, profile
    elif latin > 0:
        return TokenType.LATIN_WORD, profile
    else:
        return TokenType.UNKNOWN, profile

def tokenize_text(
    text: str,
    base_offset: int = 0
) -> List[TokenRecord]:
    """
    Tokenize normalized text into grapheme-safe TokenRecord list.
    Offsets are half-open intervals [start, end) relative to text (+ base_offset).
    """
    if not text:
        return []

    # Token pattern using Unicode extended grapheme clusters:
    # 1. Words of letters / joiners / marks (Sinhala, Latin, etc.)
    # 2. Number sequences (including decimals like 12.5)
    # 3. Discrete punctuation marks or symbols
    tokens: List[TokenRecord] = []
    grapheme_clusters = segment_graphemes(text)

    # State tracking
    current_token_clusters: List[str] = []
    current_token_start = 0
    current_char_idx = 0

    def flush_token():
        nonlocal current_token_clusters, current_token_start, current_char_idx
        if not current_token_clusters:
            return
        surface = "".join(current_token_clusters)
        token_len = len(surface)
        token_type, profile = classify_token_type(surface)

        t_record = TokenRecord(
            token_index=len(tokens),
            surface=surface,
            normalized=surface,
            token_type=token_type,
            start_code_point=base_offset + current_token_start,
            end_code_point=base_offset + current_token_start + token_len,
            grapheme_count=len(current_token_clusters),
            script_profile=profile
        )
        tokens.append(t_record)
        current_token_clusters = []

    for cluster in grapheme_clusters:
        cluster_len = len(cluster)
        first_char = cluster[0]
        cat = unicodedata.category(first_char)

        # Whitespace delimiter: flushes current token and advances
        if cat.startswith("Z") or first_char in " \t\n\r":
            flush_token()
            current_char_idx += cluster_len
            current_token_start = current_char_idx
            continue

        # Punctuation / Symbol delimiter
        is_punct_or_sym = cat.startswith("P") or cat.startswith("S") or first_char in ".,!?;:()[]{}\"'෴-"
        if is_punct_or_sym:
            # Special case: period inside numbers (decimal point)
            if first_char == "." and current_token_clusters:
                prev_text = "".join(current_token_clusters)
                if prev_text.isdigit():
                    # Could be decimal; keep with current token
                    current_token_clusters.append(cluster)
                    current_char_idx += cluster_len
                    continue

            flush_token()
            current_token_start = current_char_idx
            current_token_clusters.append(cluster)
            current_char_idx += cluster_len
            flush_token()
            current_token_start = current_char_idx
            continue

        # Letter or Number: attach to current token
        if not current_token_clusters:
            current_token_start = current_char_idx
        current_token_clusters.append(cluster)
        current_char_idx += cluster_len

    flush_token()
    return tokens
