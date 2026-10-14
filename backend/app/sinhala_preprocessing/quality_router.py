"""
Quality router module for Stage 30 Sinhala Preprocessing.
Enforces the frozen 5-level terminal disposition precedence evaluated from left to right:
  REJECTED_INVALID_UNICODE -> MANUAL_REVIEW_REQUIRED -> EXCLUDED_NON_SINHALA -> PASSED_WITH_NORMALIZATION -> PASSED
Every record receives exactly one mutually exclusive final disposition.
"""

from typing import List, Optional, Tuple
from app.sinhala_preprocessing.schemas import (
    OperationRecord,
    QualityFlag,
    TerminalDisposition
)

def resolve_terminal_disposition(
    validator_disposition: Optional[TerminalDisposition],
    validator_reason: Optional[str],
    script_disposition: Optional[TerminalDisposition],
    script_reason: Optional[str],
    quality_flags: List[QualityFlag],
    operations: List[OperationRecord]
) -> Tuple[TerminalDisposition, Optional[str]]:
    """
    Evaluate from left to right; the first matching terminal condition wins:
      1. REJECTED_INVALID_UNICODE
      2. MANUAL_REVIEW_REQUIRED
      3. EXCLUDED_NON_SINHALA
      4. PASSED_WITH_NORMALIZATION
      5. PASSED
    """
    # 1. Check for REJECTED_INVALID_UNICODE
    if validator_disposition == TerminalDisposition.REJECTED_INVALID_UNICODE:
        return TerminalDisposition.REJECTED_INVALID_UNICODE, validator_reason or "INVALID_UNICODE_DETECTED"

    if QualityFlag.PROHIBITED_CONTROL_PRESENT in quality_flags:
        return TerminalDisposition.REJECTED_INVALID_UNICODE, "PROHIBITED_CONTROL_CHARACTER"

    if QualityFlag.REPLACEMENT_CHARACTER_PRESENT in quality_flags:
        return TerminalDisposition.REJECTED_INVALID_UNICODE, "PREEXISTING_REPLACEMENT_CHARACTER"

    # 2. Check for MANUAL_REVIEW_REQUIRED
    if validator_disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, validator_reason or "MANUAL_REVIEW_TRIGGERED"

    if script_disposition == TerminalDisposition.MANUAL_REVIEW_REQUIRED:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, script_reason or "UNSUPPORTED_SCRIPT_PRESENT"

    if QualityFlag.COMBINING_SEQUENCE_REVIEW in quality_flags:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, "COMBINING_SEQUENCE_REVIEW"

    if QualityFlag.UNEXPECTED_JOINER_CONTEXT in quality_flags:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, "UNEXPECTED_JOINER_CONTEXT"

    if QualityFlag.UNSUPPORTED_SCRIPT_PRESENT in quality_flags:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, "UNSUPPORTED_SCRIPT_PRESENT"

    if QualityFlag.EMPTY_AFTER_DERIVED_WHITESPACE in quality_flags:
        return TerminalDisposition.MANUAL_REVIEW_REQUIRED, "EMPTY_AFTER_DERIVED_WHITESPACE"

    # 3. Check for EXCLUDED_NON_SINHALA
    if script_disposition == TerminalDisposition.EXCLUDED_NON_SINHALA:
        return TerminalDisposition.EXCLUDED_NON_SINHALA, script_reason or "NO_SINHALA_CONTENT"

    # 4. Check for PASSED_WITH_NORMALIZATION
    has_nfc_changes = any(op.operation_type == "UNICODE_NFC" and op.changed for op in operations)
    has_ws_changes = any(op.operation_type == "WHITESPACE_NORMALIZATION" and op.changed for op in operations)

    if has_nfc_changes or has_ws_changes or QualityFlag.NORMALIZATION_CHANGED in quality_flags:
        return TerminalDisposition.PASSED_WITH_NORMALIZATION, "NORMALIZATION_APPLIED"

    # 5. Default: PASSED
    return TerminalDisposition.PASSED, "CANONICAL_NFC"
