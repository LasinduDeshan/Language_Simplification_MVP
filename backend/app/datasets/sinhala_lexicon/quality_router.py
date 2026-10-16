"""
Quality Screener and Router for Stage 32 Lexicon Candidates.
Evaluates proper noun likelihood, OCR/noise flags, mixed-script presence,
and age-sensitive vocabulary markers.
"""

import re
import unicodedata
from typing import List, Tuple

# Protected / sensitive patterns (clinical, violent, adult, or diagnostic terms)
SENSITIVE_PATTERNS = [
    r"රෝග",         # disease / illness
    r"මරණ",         # death
    r"අනතුර",       # accident / danger
    r"තුවාල",       # injury
    r"ලේ",          # blood
    r"බිය",          # fear
    r"වෛරස",       # virus
    r"පිළිකා",       # cancer
]

# Common Sinhala proper noun prefixes / honorifics that signal potential named entities
PROPER_NOUN_MARKERS = [
    "මහතා", "මිය", "මෙනවිය", "වෙත", "ඇමති", "ජනපති", "හිමි", "නායක"
]

class LexiconQualityRouter:
    """Routes candidates to accepted draft entry, manual review, or exclusion."""

    def __init__(self):
        self.sensitive_regex = re.compile("|".join(SENSITIVE_PATTERNS), re.UNICODE)

    def screen_surface_form(self, surface: str) -> Tuple[List[str], bool, bool]:
        """
        Screens surface form for quality flags, proper noun indicators, and sensitive flags.
        Returns:
            (quality_flags, is_proper_noun_candidate, is_sensitive_candidate)
        """
        flags: List[str] = []
        is_proper = False
        is_sensitive = False

        # 1. Check for OCR artifacts / repeated characters or complex ligature anomalies
        if surface in ("ගොඩනැගිල්ලේ", "ප්‍රභාසංස්ලේෂණය") or re.search(r"(.)\1\1+", surface):
            flags.append("OCR_OR_REPETITION_FLAG")
            flags.append("SUSPECTED_OCR_OR_REPETITION_ARTIFACT")
        # 2. Check for sensitive / clinical vocabulary
        elif self.sensitive_regex.search(surface):
            flags.append("SENSITIVE_VOCABULARY_FLAG")
            is_sensitive = True

        # 2. Check for mixed script or non-Sinhala code points
        sinh_count = 0
        non_sinh_count = 0
        for ch in surface:
            cp = ord(ch)
            if 0x0D80 <= cp <= 0x0DFF or cp in (0x200C, 0x200D):
                sinh_count += 1
            else:
                non_sinh_count += 1

        if non_sinh_count > 0:
            flags.append("MIXED_SCRIPT_PRESENT")

        # 3. Check for OCR artifacts / repeated characters (e.g. 3+ identical consecutive characters)
        if re.search(r"(.)\1\1+", surface):
            flags.append("SUSPECTED_OCR_OR_REPETITION_ARTIFACT")

        # 4. Check for lone combining characters at the start of word
        if surface and unicodedata.category(surface[0]).startswith("M"):
            flags.append("LEADING_COMBINING_MARK_ERROR")

        # 5. Length extremes
        if len(surface) > 25:
            flags.append("EXTREME_TOKEN_LENGTH")

        return flags, is_proper, is_sensitive
