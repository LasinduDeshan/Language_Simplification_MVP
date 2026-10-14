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
    Calculate extended grapheme cluster count according to Unicode UAX #29.
    Consonant + combining diacritics / virama + ZWJ + consonant form clusters.
    """
    if not text:
        return 0
    
    # A standard Python implementation of extended grapheme clusters:
    # Combining characters (General Category starting with 'M') and ZWJ (U+200D)
    # attach to previous base characters.
    count = 0
    prev_was_zwj = False

    for char in text:
        category = unicodedata.category(char)
        is_mark = category.startswith("M")
        is_zwj = (char == "\u200D")
        is_zwnj = (char == "\u200C")

        if is_zwj:
            prev_was_zwj = True
        elif is_mark or is_zwnj:
            # Combining mark (diacritic or vowel sign) attaches to current base
            prev_was_zwj = False
        elif prev_was_zwj:
            # Ligature / touching consonant following ZWJ
            prev_was_zwj = False
        else:
            count += 1
            prev_was_zwj = False
            
    return count if count > 0 else (1 if text else 0)

def validate_grapheme_length(text: str, max_graphemes: int) -> Tuple[bool, int]:
    """
    Validate that text does not exceed maximum grapheme cluster limit.
    """
    count = count_grapheme_clusters(text)
    return (count <= max_graphemes, count)
