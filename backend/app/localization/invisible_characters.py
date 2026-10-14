"""
Policy enforcement for invisible, bidirectional, and control characters.
Implements the versioned control character policy: data/sinhala_foundation/registry/control_character_policy.json
"""
import re
from typing import Tuple, List, Optional
from .enums import FieldCategory

# Explicit versioned denylist code points
DENYLISTED_CHARS = {
    "\u200B",  # ZERO WIDTH SPACE
    "\u200C",  # ZERO WIDTH NON-JOINER (rejected in IDs/enums)
    "\u200D",  # ZERO WIDTH JOINER (rejected in IDs/enums)
    "\u200E",  # LEFT-TO-RIGHT MARK
    "\u200F",  # RIGHT-TO-LEFT MARK
    "\u202A",  # LEFT-TO-RIGHT EMBEDDING
    "\u202B",  # RIGHT-TO-LEFT EMBEDDING
    "\u202C",  # POP DIRECTIONAL FORMATTING
    "\u202D",  # LEFT-TO-RIGHT OVERRIDE
    "\u202E",  # RIGHT-TO-LEFT OVERRIDE
    "\u2066",  # LEFT-TO-RIGHT ISOLATE
    "\u2067",  # RIGHT-TO-LEFT ISOLATE
    "\u2068",  # FIRST STRONG ISOLATE
    "\u2069",  # POP DIRECTIONAL ISOLATE
}

# Educational text allowlisted fixture sequence controls (ZWJ and ZWNJ)
EDUCATIONAL_ALLOWLIST = {"\u200D", "\u200C"}

def validate_field_controls(
    text: str, 
    field_category: FieldCategory
) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate text against field category policy.
    Returns (is_valid, error_message, detected_characters).
    """
    if not text:
        return True, None, []

    detected_controls = []
    for char in text:
        if char in DENYLISTED_CHARS or (ord(char) < 32 and char not in "\n\r\t"):
            detected_controls.append(f"U+{ord(char):04X}")

    if field_category in [FieldCategory.IDENTIFIER, FieldCategory.USERNAME]:
        if detected_controls:
            return False, f"Denylisted control or invisible character detected in {field_category.value}: {', '.join(detected_controls)}", detected_controls
        return True, None, []

    if field_category == FieldCategory.EDUCATIONAL_TEXT:
        # Allow ZWJ and ZWNJ; reject any bidi overrides or unexpected non-printables
        invalid_for_edu = []
        for char in text:
            cp_str = f"U+{ord(char):04X}"
            if char in DENYLISTED_CHARS and char not in EDUCATIONAL_ALLOWLIST:
                invalid_for_edu.append(cp_str)
            elif ord(char) < 32 and char not in "\n\r\t":
                invalid_for_edu.append(cp_str)
        if invalid_for_edu:
            return False, f"Unexpected bidirectional or control character in educational text: {', '.join(invalid_for_edu)}", invalid_for_edu
        return True, None, detected_controls

    if field_category == FieldCategory.TECHNICAL_FIXTURE:
        # Technical fixtures preserve exact characters for round-trip testing
        return True, None, detected_controls

    return True, None, detected_controls

def escape_controls_for_log(text: str) -> str:
    """
    Escape invisible and control characters for privacy-safe logging.
    """
    if not text:
        return ""
    escaped = []
    for char in text:
        if char in DENYLISTED_CHARS or (ord(char) < 32 and char not in "\n\r\t"):
            escaped.append(f"\\u{ord(char):04x}")
        else:
            escaped.append(char)
    return "".join(escaped)
