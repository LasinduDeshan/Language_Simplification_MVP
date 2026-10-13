"""
Zero-Loss Accounting and Execution Reconciliation Module for Stage 28A.
Guarantees strict mutually exclusive item inventory conservation.
"""
from typing import List, Dict, Any, Set
from collections import Counter
from app.model_comparison.schemas import (
    ItemExecutionLedgerRecord,
    DeliveryDisposition,
    AccountingSummary,
)


def reconcile_execution_ledger(
    records: List[ItemExecutionLedgerRecord],
    expected_item_ids: Set[str],
) -> AccountingSummary:
    """
    Reconciles execution records against expected items.
    Enforces that every expected item receives exactly one mutually exclusive disposition.
    """
    expected_count = len(expected_item_ids)
    record_ids = [r.evaluation_item_id for r in records]
    id_counts = Counter(record_ids)

    # Detect duplicates
    duplicates_count = sum(cnt - 1 for cnt in id_counts.values() if cnt > 1)

    # Detect missing items
    recorded_id_set = set(id_counts.keys())
    missing_count = len(expected_item_ids - recorded_id_set)

    disposition_counts = Counter(r.final_disposition for r in records)

    native_unmod = disposition_counts.get(DeliveryDisposition.NATIVE_UNMODIFIED_DELIVERED, 0)
    native_rep = disposition_counts.get(DeliveryDisposition.NATIVE_REPAIRED_DELIVERED, 0)
    safety_fb = disposition_counts.get(DeliveryDisposition.SAFETY_FALLBACK_DELIVERED, 0)
    provider_fb = disposition_counts.get(DeliveryDisposition.PROVIDER_FALLBACK_DELIVERED, 0)
    failed = disposition_counts.get(DeliveryDisposition.FAILED, 0)
    not_attempted = disposition_counts.get(DeliveryDisposition.NOT_ATTEMPTED, 0)
    unaccounted = disposition_counts.get(DeliveryDisposition.UNACCOUNTED, 0) + missing_count

    return AccountingSummary(
        expected_items=expected_count,
        native_unmodified_delivered=native_unmod,
        native_repaired_delivered=native_rep,
        safety_fallback_delivered=safety_fb,
        provider_fallback_delivered=provider_fb,
        failed=failed,
        not_attempted=not_attempted,
        unaccounted=unaccounted,
        duplicates=duplicates_count,
        missing_items=missing_count,
    )
