"""
Script composition and language analysis module for Stage 30 Sinhala Preprocessing.
Calculates technical script distributions, flags mixed and unsupported scripts,
and enforces the governed fail-closed non-Sinhala exclusion rule.
"""

import unicodedata
from typing import Dict, List, Optional, Tuple
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

def is_sinhala_cp(cp: int) -> bool:
    return (0x0D80 <= cp <= 0x0DFF) or (0x111E1 <= cp <= 0x111F4)

def is_latin_cp(cp: int) -> bool:
    return (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F)

def is_digit_cp(cp: int) -> bool:
    return (0x0030 <= cp <= 0x0039) or (0x0DE6 <= cp <= 0x0DEF) or (0x111E1 <= cp <= 0x111F4)

class ScriptAnalysisResult:
    def __init__(
        self,
        sinhala_count: int,
        latin_count: int,
        digit_count: int,
        punctuation_count: int,
        whitespace_count: int,
        joiner_count: int,
        other_count: int,
        total_code_points: int,
        script_profile: Dict[str, float],
        flags: List[QualityFlag],
        disposition: Optional[TerminalDisposition] = None,
        reason_code: Optional[str] = None
    ):
        self.sinhala_count = sinhala_count
        self.latin_count = latin_count
        self.digit_count = digit_count
        self.punctuation_count = punctuation_count
        self.whitespace_count = whitespace_count
        self.joiner_count = joiner_count
        self.other_count = other_count
        self.total_code_points = total_code_points
        self.script_profile = script_profile
        self.flags = flags
        self.disposition = disposition
        self.reason_code = reason_code

def analyze_script_composition(
    text: str,
    declared_language: str = "si",
    declared_locale: str = "si-LK"
) -> ScriptAnalysisResult:
    total = len(text)
    if total == 0:
        return ScriptAnalysisResult(
            0, 0, 0, 0, 0, 0, 0, 0, {},
            [QualityFlag.EMPTY_AFTER_DERIVED_WHITESPACE],
            TerminalDisposition.MANUAL_REVIEW_REQUIRED,
            "EMPTY_TEXT"
        )

    sinhala = 0
    latin = 0
    digit = 0
    punct = 0
    ws = 0
    joiner = 0
    other = 0

    for char in text:
        cp = ord(char)
        cat = unicodedata.category(char)

        if cp in (0x200D, 0x200C):
            joiner += 1
        elif is_sinhala_cp(cp):
            sinhala += 1
        elif is_latin_cp(cp):
            latin += 1
        elif is_digit_cp(cp):
            digit += 1
        elif cat.startswith("P") or cp in (0x0DF4,):
            punct += 1
        elif cat.startswith("Z") or cp in (0x0A, 0x0D, 0x09):
            ws += 1
        else:
            other += 1

    profile = {
        "Sinh": round(sinhala / total, 4),
        "Latn": round(latin / total, 4),
        "Digit": round(digit / total, 4),
        "Punct": round(punct / total, 4),
        "Other": round(other / total, 4)
    }

    flags: List[QualityFlag] = []
    if joiner > 0:
        flags.append(QualityFlag.JOINER_PRESENT)

    if latin > 0 and sinhala > 0:
        flags.append(QualityFlag.MIXED_SCRIPT_PRESENT)

    if other > 0:
        flags.append(QualityFlag.UNSUPPORTED_SCRIPT_PRESENT)

    # Governed exclusion logic:
    # EXCLUDED_NON_SINHALA applies ONLY if trusted metadata does not claim Sinhala
    # AND there is zero Sinhala content detected.
    is_declared_sinhala = declared_language.lower() in ("si", "si-lk") or "si" in declared_locale.lower()

    if not is_declared_sinhala and sinhala == 0:
        return ScriptAnalysisResult(
            sinhala, latin, digit, punct, ws, joiner, other, total, profile, flags,
            TerminalDisposition.EXCLUDED_NON_SINHALA,
            "NO_SINHALA_CONTENT"
        )

    # If unsupported script is present, route to MANUAL_REVIEW_REQUIRED
    if other > 0:
        return ScriptAnalysisResult(
            sinhala, latin, digit, punct, ws, joiner, other, total, profile, flags,
            TerminalDisposition.MANUAL_REVIEW_REQUIRED,
            "UNSUPPORTED_SCRIPT_PRESENT"
        )

    return ScriptAnalysisResult(
        sinhala, latin, digit, punct, ws, joiner, other, total, profile, flags,
        None,
        None
    )
