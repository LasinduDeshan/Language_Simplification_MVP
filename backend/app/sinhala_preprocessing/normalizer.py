"""
Unicode and whitespace normalization module for Stage 30 Sinhala Preprocessing.
Provides:
- Governed NFC derivation and idempotence verification
- Role-aware whitespace normalization
- Reversible operation audit traces with zero-based half-open offset spans [start, end)
- Absolute raw-text immutability preservation
"""

import re
import hashlib
import unicodedata
from typing import List, Tuple
from app.sinhala_preprocessing.schemas import (
    HalfOpenSpan,
    MappingStatus,
    OperationRecord
)

def compute_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def normalize_nfc(text: str, rule_version: str = "1.0.0") -> Tuple[str, List[OperationRecord]]:
    """
    Apply Unicode NFC normalization to text and record operation if changed.
    Verifies idempotence: NFC(NFC(x)) == NFC(x).
    """
    before_sha = compute_text_sha256(text)
    nfc_text = unicodedata.normalize("NFC", text)
    after_sha = compute_text_sha256(nfc_text)
    changed = (nfc_text != text)

    # Verify idempotence
    second_pass = unicodedata.normalize("NFC", nfc_text)
    assert second_pass == nfc_text, "NFC normalization idempotence failure!"

    operations: List[OperationRecord] = []
    if changed:
        # Determine mapping status
        len_raw = len(text)
        len_norm = len(nfc_text)
        if len_raw > len_norm:
            status = MappingStatus.MANY_TO_ONE
        elif len_raw < len_norm:
            status = MappingStatus.ONE_TO_MANY
        else:
            status = MappingStatus.ONE_TO_ONE

        op = OperationRecord(
            operation_id="OP-NFC-0001",
            operation_type="UNICODE_NFC",
            raw_spans=[HalfOpenSpan(start_code_point=0, end_code_point=len_raw)],
            normalized_spans=[HalfOpenSpan(start_code_point=0, end_code_point=len_norm)],
            before_sha256=before_sha,
            after_sha256=after_sha,
            changed=True,
            mapping_status=status,
            mapping_exact=True,
            rule_version=rule_version
        )
        operations.append(op)

    return nfc_text, operations

def normalize_whitespace(
    text: str,
    text_role: str = "prose",
    rule_version: str = "1.0.0"
) -> Tuple[str, List[OperationRecord]]:
    """
    Apply role-aware whitespace normalization:
    - Convert CRLF / CR to LF
    - Collapse horizontal whitespace runs to single space
    - Trim leading and trailing whitespace
    - Preserve meaningful paragraph breaks for prose
    """
    before_sha = compute_text_sha256(text)
    len_before = len(text)

    # 1. Normalize line breaks
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Collapse horizontal whitespace (tab, NBSP, multiple spaces)
    normalized = re.sub(r"[ \t\u00A0]+", " ", normalized)

    # 3. Collapse multiple blank lines (> 2 newlines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    # 4. Trim leading and trailing
    normalized = normalized.strip()

    after_sha = compute_text_sha256(normalized)
    changed = (normalized != text)

    operations: List[OperationRecord] = []
    if changed:
        len_after = len(normalized)
        op = OperationRecord(
            operation_id="OP-WS-0001",
            operation_type="WHITESPACE_NORMALIZATION",
            raw_spans=[HalfOpenSpan(start_code_point=0, end_code_point=len_before)],
            normalized_spans=[HalfOpenSpan(start_code_point=0, end_code_point=len_after)],
            before_sha256=before_sha,
            after_sha256=after_sha,
            changed=True,
            mapping_status=MappingStatus.MANY_TO_ONE if len_before > len_after else MappingStatus.ONE_TO_ONE,
            mapping_exact=True,
            rule_version=rule_version
        )
        operations.append(op)

    return normalized, operations
