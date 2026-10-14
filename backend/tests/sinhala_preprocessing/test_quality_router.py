"""
Tests for Stage 30 Quality Router and Terminal Disposition Precedence.
"""

from app.sinhala_preprocessing.quality_router import resolve_terminal_disposition
from app.sinhala_preprocessing.schemas import (
    OperationRecord,
    QualityFlag,
    TerminalDisposition
)

def test_frozen_precedence_rejection_over_review():
    # If both invalid control and suspicious combining sequence are present, REJECTED wins
    flags = [QualityFlag.PROHIBITED_CONTROL_PRESENT, QualityFlag.COMBINING_SEQUENCE_REVIEW]
    disp, reason = resolve_terminal_disposition(
        validator_disposition=TerminalDisposition.REJECTED_INVALID_UNICODE,
        validator_reason="PROHIBITED_CONTROL_CHARACTER",
        script_disposition=TerminalDisposition.MANUAL_REVIEW_REQUIRED,
        script_reason="COMBINING_SEQUENCE_REVIEW",
        quality_flags=flags,
        operations=[]
    )
    assert disp == TerminalDisposition.REJECTED_INVALID_UNICODE

def test_frozen_precedence_review_over_normalization():
    # If text required review and normalization, MANUAL_REVIEW_REQUIRED wins
    flags = [QualityFlag.UNEXPECTED_JOINER_CONTEXT, QualityFlag.NORMALIZATION_CHANGED]
    disp, reason = resolve_terminal_disposition(
        validator_disposition=TerminalDisposition.MANUAL_REVIEW_REQUIRED,
        validator_reason="UNEXPECTED_JOINER_CONTEXT",
        script_disposition=None,
        script_reason=None,
        quality_flags=flags,
        operations=[]
    )
    assert disp == TerminalDisposition.MANUAL_REVIEW_REQUIRED

def test_frozen_precedence_normalization_over_passed():
    # If NFC changes occurred, PASSED_WITH_NORMALIZATION wins over PASSED
    flags = [QualityFlag.NORMALIZATION_CHANGED]
    disp, reason = resolve_terminal_disposition(
        validator_disposition=None,
        validator_reason=None,
        script_disposition=None,
        script_reason=None,
        quality_flags=flags,
        operations=[]
    )
    assert disp == TerminalDisposition.PASSED_WITH_NORMALIZATION

def test_frozen_precedence_passed_default():
    # Clean text with no changes resolves to PASSED
    disp, reason = resolve_terminal_disposition(
        validator_disposition=None,
        validator_reason=None,
        script_disposition=None,
        script_reason=None,
        quality_flags=[],
        operations=[]
    )
    assert disp == TerminalDisposition.PASSED
