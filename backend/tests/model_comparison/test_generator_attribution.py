"""
Test mutually exclusive delivery attribution and ledger record invariants.
"""
import pytest
from app.model_comparison.schemas import (
    DeliveryDisposition,
    ItemExecutionLedgerRecord,
    AccountingSummary,
)
from app.model_comparison.attribution import (
    resolve_delivery_disposition,
    validate_ledger_record_invariants,
    compute_sha256,
    EMPTY_STRING_SHA256,
)


def test_resolve_disposition_mutually_exclusive():
    # 1. Native unmodified
    d1 = resolve_delivery_disposition(
        native_received=True,
        repaired=False,
        fallback_used=False,
        fallback_reason=None,
        validation_passed=True,
        execution_succeeded=True,
    )
    assert d1 == DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED

    # 2. Native repaired
    d2 = resolve_delivery_disposition(
        native_received=True,
        repaired=True,
        fallback_used=False,
        fallback_reason=None,
        validation_passed=True,
        execution_succeeded=True,
    )
    assert d2 == DeliveryDisposition.NATIVE_REPAIRED_DELIVERED

    # 3. Safety fallback
    d3 = resolve_delivery_disposition(
        native_received=False,
        repaired=False,
        fallback_used=True,
        fallback_reason="meaning_preservation_failure: entity missing",
        validation_passed=True,
        execution_succeeded=True,
    )
    assert d3 == DeliveryDisposition.SAFETY_FALLBACK_DELIVERED

    # 4. Provider fallback (quota/429)
    d4 = resolve_delivery_disposition(
        native_received=False,
        repaired=False,
        fallback_used=True,
        fallback_reason="HTTP 429: Quota exceeded",
        validation_passed=True,
        execution_succeeded=True,
    )
    assert d4 == DeliveryDisposition.PROVIDER_FALLBACK_DELIVERED

    # 5. Failed
    d5 = resolve_delivery_disposition(
        native_received=False,
        repaired=False,
        fallback_used=False,
        fallback_reason=None,
        validation_passed=False,
        execution_succeeded=False,
    )
    assert d5 == DeliveryDisposition.FAILED

    # 6. Not attempted
    d6 = resolve_delivery_disposition(
        native_received=False,
        repaired=False,
        fallback_used=False,
        fallback_reason=None,
        validation_passed=False,
        execution_succeeded=False,
        not_attempted=True,
    )
    assert d6 == DeliveryDisposition.NOT_ATTEMPTED


def test_native_output_invariants_reject_empty():
    # Reject empty string when native_output_received is True
    rec = ItemExecutionLedgerRecord(
        evaluation_item_id="TEST-001",
        source_group_id="SG-001",
        support_level="mild",
        requested_system="G1",
        generator_attribution="native_gemini",
        final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        native_output_received=True,
        output_text="",
        output_sha256=EMPTY_STRING_SHA256,
    )
    valid, err = validate_ledger_record_invariants(rec)
    assert valid is False
    assert "empty" in err

    # Reject empty hash
    rec2 = ItemExecutionLedgerRecord(
        evaluation_item_id="TEST-001",
        source_group_id="SG-001",
        support_level="mild",
        requested_system="G1",
        generator_attribution="native_gemini",
        final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        native_output_received=True,
        output_text="Valid output text",
        output_sha256=EMPTY_STRING_SHA256,
    )
    valid2, err2 = validate_ledger_record_invariants(rec2)
    assert valid2 is False

    # Accept valid non-empty output with matching hash
    valid_text = "The cat ran away."
    valid_hash = compute_sha256(valid_text)
    rec3 = ItemExecutionLedgerRecord(
        evaluation_item_id="TEST-001",
        source_group_id="SG-001",
        support_level="mild",
        requested_system="G1",
        generator_attribution="native_gemini",
        final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        native_output_received=True,
        output_text=valid_text,
        output_sha256=valid_hash,
    )
    valid3, err3 = validate_ledger_record_invariants(rec3)
    assert valid3 is True
    assert err3 is None


def test_accounting_summary_conservation():
    summary = AccountingSummary(
        expected_items=135,
        native_unmodified_delivered=110,
        native_repaired_delivered=15,
        safety_fallback_delivered=7,
        provider_fallback_delivered=3,
        failed=0,
        not_attempted=0,
        unaccounted=0,
        duplicates=0,
        missing_items=0,
    )
    assert summary.is_strictly_conserved is True
    assert summary.total_delivered == 135
    assert summary.total_accounted == 135

    # Conservation fails if items are unaccounted
    summary_leaked = AccountingSummary(
        expected_items=135,
        native_unmodified_delivered=110,
        native_repaired_delivered=15,
        safety_fallback_delivered=7,
        provider_fallback_delivered=0,
        failed=0,
        not_attempted=0,
        unaccounted=3,
    )
    assert summary_leaked.is_strictly_conserved is False
