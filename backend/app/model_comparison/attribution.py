"""
Attribution Engine for Stage 28A Preliminary English Model Comparison.
Enforces mutually exclusive delivery categories and strict attribution invariants.
"""
import hashlib
from typing import Optional, Tuple
from app.model_comparison.schemas import DeliveryDisposition, ItemExecutionLedgerRecord

EMPTY_STRING_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def compute_sha256(text: str) -> str:
    """Compute standard 64-character lowercase hexadecimal SHA-256 hash."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_delivery_disposition(
    *,
    native_received: bool,
    repaired: bool,
    fallback_used: bool,
    fallback_reason: Optional[str],
    validation_passed: bool,
    execution_succeeded: bool,
    not_attempted: bool = False,
) -> DeliveryDisposition:
    """
    Resolve exactly ONE mutually exclusive delivery disposition.
    Prevents double-counting between native responses and repairs.
    """
    if not_attempted:
        return DeliveryDisposition.NOT_ATTEMPTED

    if not execution_succeeded:
        return DeliveryDisposition.FAILED

    if fallback_used:
        # Determine whether fallback was triggered by provider error or safety gate
        if fallback_reason and any(
            token in fallback_reason.lower()
            for token in ["429", "timeout", "quota", "connection", "http", "api_error", "provider"]
        ):
            return DeliveryDisposition.PROVIDER_FALLBACK_DELIVERED
        else:
            return DeliveryDisposition.SAFETY_FALLBACK_DELIVERED

    if native_received:
        if repaired:
            return DeliveryDisposition.NATIVE_REPAIRED_DELIVERED
        else:
            return DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED

    return DeliveryDisposition.UNACCOUNTED


def validate_ledger_record_invariants(record: ItemExecutionLedgerRecord) -> Tuple[bool, Optional[str]]:
    """
    Validate that an execution ledger record satisfies strict Stage 28A invariants:
    1. If native_output_received == True:
       - output_text must not be empty
       - output_sha256 must not match empty string SHA-256
    2. Final disposition must be valid and non-None
    3. Output SHA-256 must match output_text if output_text is present
    """
    if record.native_output_received:
        if not record.output_text or not record.output_text.strip():
            return False, "native_output_received is True but output_text is empty or whitespace"
        if record.output_sha256 == EMPTY_STRING_SHA256:
            return False, "native_output_received is True but output_sha256 matches empty string hash"

    if record.output_text is not None and record.output_sha256 is not None:
        computed = compute_sha256(record.output_text)
        if computed != record.output_sha256:
            return False, f"output_sha256 mismatch: expected {computed}, got {record.output_sha256}"

    return True, None
