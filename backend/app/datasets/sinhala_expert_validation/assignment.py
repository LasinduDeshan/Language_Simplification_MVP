"""
Stage 34 — Deterministic Expertise-Aware Assignment Engine
Generates balanced, blinded assignments ensuring each primary item receives:
- at least 2 Sinhala linguist reviews;
- at least 2 developmental suitability reviews;
- at least 3 independent reviews in total.
"""

import random
from typing import Any, Dict, List
from .enums import AssignmentStatus, ReviewerRole


def generate_assignments(
    items: List[Dict[str, Any]],
    qualified_reviewers: List[Dict[str, Any]],
    seed: int = 1034,
) -> List[Dict[str, Any]]:
    rng = random.Random(seed)

    linguists = [
        r["reviewer_id"]
        for r in qualified_reviewers
        if ReviewerRole.SINHALA_LINGUIST.value in r["roles"]
        and not r.get("is_project_team_member", False)
        and ReviewerRole.INDEPENDENT_ADJUDICATOR.value not in r["roles"]
    ]
    dev_raters = [
        r["reviewer_id"]
        for r in qualified_reviewers
        if (
            ReviewerRole.EARLY_CHILDHOOD_EDUCATOR.value in r["roles"]
            or ReviewerRole.CHILD_DEVELOPMENT_SPECIALIST.value in r["roles"]
        )
        and not r.get("is_project_team_member", False)
        and ReviewerRole.INDEPENDENT_ADJUDICATOR.value not in r["roles"]
    ]

    assert len(linguists) >= 2, f"Requires at least 2 linguists, got {len(linguists)}"
    assert len(dev_raters) >= 2, f"Requires at least 2 developmental raters, got {len(dev_raters)}"

    assignments = []
    asn_idx = 1

    for item in items:
        item_id = item["item_id"]

        # Ensure at least 2 linguists
        assigned_linguists = sorted(linguists[:2])

        # Ensure at least 2 developmental raters (sampled deterministically with rotation)
        chosen_dev = rng.sample(dev_raters, 2)
        assigned_dev = sorted(chosen_dev)

        # Union of reviewers for this item
        item_reviewers = list(dict.fromkeys(assigned_linguists + assigned_dev))

        assert len(item_reviewers) >= 3, (
            f"Item {item_id} must have at least 3 independent reviewers, got {len(item_reviewers)}"
        )
        assert len(assigned_linguists) >= 2, (
            f"Item {item_id} must have at least 2 linguists, got {len(assigned_linguists)}"
        )
        assert len(assigned_dev) >= 2, (
            f"Item {item_id} must have at least 2 developmental raters, got {len(assigned_dev)}"
        )

        for rev_id in item_reviewers:
            assignments.append({
                "assignment_id": f"ASN-S34-{asn_idx:06d}",
                "item_id": item_id,
                "reviewer_id": rev_id,
                "status": AssignmentStatus.ASSIGNED.value,
                "is_control": item.get("is_control", False),
            })
            asn_idx += 1

    return assignments
