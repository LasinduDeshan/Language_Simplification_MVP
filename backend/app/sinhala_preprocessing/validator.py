"""
Unicode validation module for Stage 30 Sinhala Preprocessing.
Performs fail-closed security and orthographic validation:
- Prohibited control characters (C0, C1, bidi overrides, null bytes)
- Replacement character U+FFFD detection and source-fidelity classification
- Unattached combining marks
- Excessive repeated combining marks
- ZWJ/ZWNJ context checking against governed allowlists
"""

import unicodedata
from typing import List, Optional, Set, Tuple
from app.sinhala_preprocessing.schemas import QualityFlag, TerminalDisposition

PROHIBITED_BIDI_CONTROLS: Set[int] = {
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # Bidi overrides/embeddings
    0x2066, 0x2067, 0x2068, 0x2069            # Bidi isolates
}

ALLOWED_WHITESPACE_CPS: Set[int] = {0x0009, 0x000A, 0x000D, 0x0020, 0x00A0}

REPLACEMENT_CHARACTER = "\uFFFD"

def is_prohibited_control(char: str) -> bool:
    cp = ord(char)
    if cp in ALLOWED_WHITESPACE_CPS:
        return False
    if cp in PROHIBITED_BIDI_CONTROLS:
        return True
    if cp == 0x0000:
        return True
    if 0x0001 <= cp <= 0x001F:
        return True
    if 0x007F <= cp <= 0x009F:
        return True
    category = unicodedata.category(char)
    if category == "Cc":
        return True
    return False

def is_unattached_combining_mark(text: str, idx: int) -> bool:
    char = text[idx]
    category = unicodedata.category(char)
    if not category.startswith("M"):
        return False
    if idx == 0:
        return True
    prev_char = text[idx - 1]
    prev_cat = unicodedata.category(prev_char)
    # A combining mark must attach to a letter, number, or previous combining mark
    if not (prev_cat.startswith("L") or prev_cat.startswith("N") or prev_cat.startswith("M")):
        return True
    return False

def validate_joiner_context(text: str, idx: int) -> bool:
    """
    Check whether a ZWJ (U+200D) or ZWNJ (U+200C) appears in an allowlisted Sinhala context.
    Allowlisted ZWJ contexts:
      - Yansaya: Consonant + Virama (U+0DCA) + ZWJ + Ya (U+0DBF)
      - Rakaransaya: Consonant + Virama (U+0DCA) + ZWJ + Ra (U+0DBB)
      - Bandi-akuru (Conjuncts): Consonant + Virama (U+0DCA) + ZWJ + Consonant
      - Repaya: Ra (U+0DBB) + Virama (U+0DCA) + ZWJ + Consonant
    """
    char = text[idx]
    if char not in ("\u200D", "\u200C"):
        return True

    # ZWJ at text boundaries is always unexpected
    if idx == 0 or idx >= len(text) - 1:
        return False

    prev_char = text[idx - 1]
    next_char = text[idx + 1]

    # Preceding char must be virama U+0DCA
    if prev_char != "\u0DCA":
        return False

    # Following char must be a Sinhala consonant
    next_cp = ord(next_char)
    is_sinhala_consonant = (0x0D9A <= next_cp <= 0x0DC6)
    if not is_sinhala_consonant:
        return False

    # Before the virama, must have a Sinhala consonant or letter
    if idx < 2:
        return False
    base_char = text[idx - 2]
    base_cp = ord(base_char)
    is_base_consonant = (0x0D9A <= base_cp <= 0x0DC6) or (0x0D85 <= base_cp <= 0x0D96)
    return is_base_consonant

class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        flags: List[QualityFlag],
        disposition: Optional[TerminalDisposition] = None,
        reason_code: Optional[str] = None
    ):
        self.is_valid = is_valid
        self.flags = flags
        self.disposition = disposition
        self.reason_code = reason_code

def validate_unicode_text(text: str) -> ValidationResult:
    flags: List[QualityFlag] = []

    if not text or text.strip() == "":
        flags.append(QualityFlag.EMPTY_AFTER_DERIVED_WHITESPACE)
        return ValidationResult(
            is_valid=False,
            flags=flags,
            disposition=TerminalDisposition.MANUAL_REVIEW_REQUIRED,
            reason_code="EMPTY_OR_WHITESPACE_ONLY"
        )

    # 1. Replacement character check
    if REPLACEMENT_CHARACTER in text:
        flags.append(QualityFlag.REPLACEMENT_CHARACTER_PRESENT)
        return ValidationResult(
            is_valid=False,
            flags=flags,
            disposition=TerminalDisposition.REJECTED_INVALID_UNICODE,
            reason_code="PREEXISTING_REPLACEMENT_CHARACTER"
        )

    # 2. Check for prohibited control characters
    for idx, char in enumerate(text):
        if is_prohibited_control(char):
            flags.append(QualityFlag.PROHIBITED_CONTROL_PRESENT)
            return ValidationResult(
                is_valid=False,
                flags=flags,
                disposition=TerminalDisposition.REJECTED_INVALID_UNICODE,
                reason_code="PROHIBITED_CONTROL_CHARACTER"
            )

    # 3. Check for unattached combining marks and excessive marks
    combining_run = 0
    for idx, char in enumerate(text):
        cat = unicodedata.category(char)
        is_mark = cat.startswith("M")
        if is_mark:
            combining_run += 1
            if is_unattached_combining_mark(text, idx):
                if QualityFlag.COMBINING_SEQUENCE_REVIEW not in flags:
                    flags.append(QualityFlag.COMBINING_SEQUENCE_REVIEW)
            if combining_run > 3:
                if QualityFlag.COMBINING_SEQUENCE_REVIEW not in flags:
                    flags.append(QualityFlag.COMBINING_SEQUENCE_REVIEW)
        else:
            combining_run = 0

    # 4. Check ZWJ / ZWNJ contexts
    for idx, char in enumerate(text):
        if char in ("\u200D", "\u200C"):
            if QualityFlag.JOINER_PRESENT not in flags:
                flags.append(QualityFlag.JOINER_PRESENT)
            if not validate_joiner_context(text, idx):
                if QualityFlag.UNEXPECTED_JOINER_CONTEXT not in flags:
                    flags.append(QualityFlag.UNEXPECTED_JOINER_CONTEXT)

    # If flags require manual review, report so
    if QualityFlag.UNEXPECTED_JOINER_CONTEXT in flags:
        return ValidationResult(
            is_valid=True,
            flags=flags,
            disposition=TerminalDisposition.MANUAL_REVIEW_REQUIRED,
            reason_code="UNEXPECTED_JOINER_CONTEXT"
        )
    if QualityFlag.COMBINING_SEQUENCE_REVIEW in flags:
        return ValidationResult(
            is_valid=True,
            flags=flags,
            disposition=TerminalDisposition.MANUAL_REVIEW_REQUIRED,
            reason_code="COMBINING_SEQUENCE_REVIEW"
        )

    return ValidationResult(
        is_valid=True,
        flags=flags,
        disposition=None,
        reason_code=None
    )
