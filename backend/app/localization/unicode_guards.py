"""
Unicode guards for Stage 29 round-trip fidelity, replacement character detection,
and grapheme cluster limit calculations.
"""
import unicodedata
from typing import List, Tuple

REPLACEMENT_CHARACTER = "\uFFFD"

def extract_code_points(text: str) -> List[str]:
    """
    Return list of formatted Unicode code points (e.g. ['U+0D9A', 'U+0DCA']).
    """
    return [f"U+{ord(c):04X}" for c in text]

def verify_code_point_equality(input_text: str, output_text: str) -> Tuple[bool, List[str], List[str]]:
    """
    Verify exact decoded code-point sequence equality across boundaries.
    """
    in_cps = extract_code_points(input_text)
    out_cps = extract_code_points(output_text)
    return (in_cps == out_cps, in_cps, out_cps)

def has_replacement_character(text: str) -> bool:
    """
    Detect whether Unicode replacement character U+FFFD was introduced.
    """
    return REPLACEMENT_CHARACTER in text

def count_grapheme_clusters(text: str) -> int:
    """
    Project-defined grapheme counter using Python unicodedata properties.
    Verified scope: 11/11 governed Stage 29 fixtures matched frontend Intl.Segmenter.
    Full Unicode UAX #29 conformance: NOT ESTABLISHED.
    Combining characters, vowel signs, viramas, and ZWJ attach to previous base characters.
    """
    if not text:
        return 0

    count = 0
    in_cluster = False

    for char in text:
        cp = ord(char)
        category = unicodedata.category(char)
        is_mark = category.startswith("M")
        is_zwj = (char == "\u200D")
        is_zwnj = (char == "\u200C")
        is_sinhala_mark = (0x0DCA <= cp <= 0x0DF3) or (cp in (0x0D82, 0x0D83))
        is_combining = is_mark or is_sinhala_mark or is_zwj or is_zwnj

        if is_combining:
            if not in_cluster:
                count += 1
                in_cluster = True
        else:
            count += 1
            in_cluster = True

    return count

def validate_grapheme_length(text: str, max_graphemes: int) -> Tuple[bool, int]:
    """
    Validate that text does not exceed maximum grapheme cluster limit.
    """
    count = count_grapheme_clusters(text)
    return (count <= max_graphemes, count)
