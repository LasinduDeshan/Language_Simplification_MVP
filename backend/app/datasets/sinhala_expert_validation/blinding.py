"""
Stage 34 — Review Blinding Service
Strips split membership, rule IDs, candidate rank, expected disposition, and control flags
so that reviewers evaluate text candidates without biasing cues.
"""

from typing import Any, Dict


def blind_item_for_reviewer(item: Dict[str, Any], reviewer_id: str) -> Dict[str, Any]:
    """Returns a strictly blinded item representation for an assigned reviewer."""
    # Never expose split, applied_rule_ids, rank, or control status
    return {
        "item_id": item["item_id"],
        "assigned_reviewer_id": reviewer_id,
        "source_storage_ref": item.get("source_storage_ref"),
        "candidate_storage_ref": item.get("output_storage_ref"),
        "language": "si",
        "locale": "si-LK",
        "target_age_band": "4-8",
    }
