"""
Sentence segmentation module for Stage 30 Sinhala Preprocessing.
Provides deterministic, rule-based segmentation with protection for:
- Decimal numbers (e.g. 12.5)
- Common Sinhala and Latin abbreviations (e.g. වෛ., පෙ.ව., Dr., e.g.)
- Repeated punctuation runs (e.g. ...)
Returns SentenceRecord list with zero-based half-open code-point intervals.
"""

import re
import hashlib
from typing import List, Tuple
from app.sinhala_preprocessing.schemas import SentenceRecord

DEFAULT_ABBREVIATIONS = {
    "වෛ.", "මහා.", "පෙ.ව.", "ප.ව.", "පිටු.", "රු.", "ඩො.",
    "e.g.", "i.e.", "etc.", "Dr.", "Mr.", "Mrs.", "Prof.", "No."
}

def is_decimal_point(text: str, idx: int) -> bool:
    """
    Check if a period at idx is a decimal point between two digits.
    """
    if text[idx] != ".":
        return False
    if idx > 0 and idx < len(text) - 1:
        prev_char = text[idx - 1]
        next_char = text[idx + 1]
        if prev_char.isdigit() and next_char.isdigit():
            return True
    return False

def matches_abbreviation(text: str, period_idx: int, abbreviations=DEFAULT_ABBREVIATIONS) -> bool:
    """
    Check if the text ending at period_idx matches any known abbreviation.
    """
    for abbr in abbreviations:
        abbr_len = len(abbr)
        start_idx = period_idx - abbr_len + 1
        if start_idx >= 0 and text[start_idx:period_idx + 1] == abbr:
            # Check left boundary: start of text, space, or punctuation
            if start_idx == 0 or text[start_idx - 1] in " \t\n([{":
                return True
    return False

def is_repeated_punct(text: str, idx: int) -> bool:
    """
    Check if punctuation at idx is part of an ongoing run (e.g. '..' or '?!').
    """
    char = text[idx]
    if char not in ".?!":
        return False
    # If the next character is also a punctuation mark, it's not the final split point
    if idx + 1 < len(text) and text[idx + 1] in ".?!":
        return True
    return False

def segment_sentences(
    text: str,
    abbreviations=DEFAULT_ABBREVIATIONS
) -> List[SentenceRecord]:
    """
    Segment normalized text into discrete sentences with [start_code_point, end_code_point) intervals.
    """
    if not text:
        return []

    sentences: List[SentenceRecord] = []
    n = len(text)
    start = 0
    idx = 0

    while idx < n:
        char = text[idx]
        boundary_rule = None

        # Check paragraph breaks (two newlines)
        if char == "\n" and idx + 1 < n and text[idx + 1] == "\n":
            boundary_rule = "PARAGRAPH_BREAK"
            split_end = idx
            next_start = idx + 2

        # Check punctuation boundaries (. ? ! ෴)
        elif char in (".", "?", "!", "\u0DF4"):
            # Check false boundary conditions
            if char == "." and is_decimal_point(text, idx):
                idx += 1
                continue
            if char == "." and matches_abbreviation(text, idx, abbreviations):
                idx += 1
                continue
            if is_repeated_punct(text, idx):
                idx += 1
                continue

            # Valid terminal boundary found
            if char == ".":
                boundary_rule = "FULL_STOP"
            elif char == "?":
                boundary_rule = "QUESTION_MARK"
            elif char == "!":
                boundary_rule = "EXCLAMATION_MARK"
            elif char == "\u0DF4":
                boundary_rule = "KUNDDALIYA"

            split_end = idx + 1
            next_start = idx + 1
            # Skip subsequent whitespace for next start
            while next_start < n and text[next_start] in " \t\n":
                next_start += 1

        if boundary_rule:
            span_text = text[start:split_end].strip()
            if span_text:
                s_record = SentenceRecord(
                    sentence_index=len(sentences),
                    text=span_text,
                    start_code_point=start,
                    end_code_point=split_end,
                    boundary_rule=boundary_rule,
                    sha256=hashlib.sha256(span_text.encode("utf-8")).hexdigest()
                )
                sentences.append(s_record)
            start = next_start
            idx = next_start
        else:
            idx += 1

    # Final sentence if text remains after last boundary
    if start < n:
        span_text = text[start:n].strip()
        if span_text:
            s_record = SentenceRecord(
                sentence_index=len(sentences),
                text=span_text,
                start_code_point=start,
                end_code_point=n,
                boundary_rule="END_OF_TEXT",
                sha256=hashlib.sha256(span_text.encode("utf-8")).hexdigest()
            )
            sentences.append(s_record)

    return sentences
