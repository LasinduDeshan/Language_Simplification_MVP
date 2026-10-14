"""
Test zero-loss inventory accounting and strict conservation invariants.
"""
import pytest
from app.model_comparison.schemas import (
    ItemExecutionLedgerRecord,
    DeliveryDisposition,
)
from app.model_comparison.accounting import reconcile_execution_ledger


def test_reconciliation_zero_loss():
    expected_ids = {f"ITEM-{i:03d}" for i in range(1, 101)}

    records = []
    # 70 native unmodified
    for i in range(1, 71):
        records.append(
            ItemExecutionLedgerRecord(
                evaluation_item_id=f"ITEM-{i:03d}",
                source_group_id=f"SG-{i:03d}",
                support_level="moderate",
                requested_system="H1",
                generator_attribution="native_gemini",
                final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
                native_output_received=True,
                output_text="Sample text",
                output_sha256="valid_hash",
            )
        )
    # 20 native repaired
    for i in range(71, 91):
        records.append(
            ItemExecutionLedgerRecord(
                evaluation_item_id=f"ITEM-{i:03d}",
                source_group_id=f"SG-{i:03d}",
                support_level="moderate",
                requested_system="H1",
                generator_attribution="native_gemini_repaired",
                final_disposition=DeliveryDisposition.NATIVE_REPAIRED_DELIVERED,
                native_output_received=True,
                repair_used=True,
                output_text="Repaired sample text",
                output_sha256="valid_hash_rep",
            )
        )
    # 10 safety fallback
    for i in range(91, 101):
        records.append(
            ItemExecutionLedgerRecord(
                evaluation_item_id=f"ITEM-{i:03d}",
                source_group_id=f"SG-{i:03d}",
                support_level="moderate",
                requested_system="H1",
                generator_attribution="stage25_fallback",
                final_disposition=DeliveryDisposition.SAFETY_FALLBACK_DELIVERED,
                fallback_used=True,
                fallback_reason="entity_loss",
                output_text="Fallback sample text",
                output_sha256="valid_hash_fb",
            )
        )

    summary = reconcile_execution_ledger(records, expected_ids)
    assert summary.expected_items == 100
    assert summary.native_unmodified_delivered == 70
    assert summary.native_repaired_delivered == 20
    assert summary.safety_fallback_delivered == 10
    assert summary.failed == 0
    assert summary.not_attempted == 0
    assert summary.unaccounted == 0
    assert summary.duplicates == 0
    assert summary.missing_items == 0
    assert summary.is_strictly_conserved is True


def test_reconciliation_detects_missing_and_duplicates():
    expected_ids = {"ITEM-001", "ITEM-002", "ITEM-003"}

    # Pass ITEM-001 twice, omit ITEM-003
    records = [
        ItemExecutionLedgerRecord(
            evaluation_item_id="ITEM-001",
            source_group_id="SG-001",
            support_level="mild",
            requested_system="H1",
            generator_attribution="native",
            final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        ),
        ItemExecutionLedgerRecord(
            evaluation_item_id="ITEM-001",
            source_group_id="SG-001",
            support_level="mild",
            requested_system="H1",
            generator_attribution="native",
            final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        ),
        ItemExecutionLedgerRecord(
            evaluation_item_id="ITEM-002",
            source_group_id="SG-002",
            support_level="mild",
            requested_system="H1",
            generator_attribution="native",
            final_disposition=DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED,
        ),
    ]

    summary = reconcile_execution_ledger(records, expected_ids)
    assert summary.duplicates == 1
    assert summary.missing_items == 1
    assert summary.is_strictly_conserved is False
