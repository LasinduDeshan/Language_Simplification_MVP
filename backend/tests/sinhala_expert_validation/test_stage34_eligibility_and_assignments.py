"""
Unit tests for Stage 34 reviewer eligibility and expertise-aware assignments.
Validates:
1. Reviewer panel meets minimum 6 unique individuals + conflict checks;
2. Dual-competency quota: every item receives >= 2 linguists and >= 2 developmental raters;
3. Exactly 600 assignments generated across 150 items.
"""

import json
from pathlib import Path
import pytest

from app.datasets.sinhala_expert_validation.assignment import generate_assignments
from app.datasets.sinhala_expert_validation.enums import ReviewerRole
from scripts.stage34.build_annotation_items import setup_panel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation"
ASSIGNMENT_FILE = DATA_DIR / "assignments" / "assignment_ledger.jsonl"


def test_reviewer_panel_diversity_and_eligibility():
    registry = setup_panel()
    panel_check = registry.verify_panel_composition()

    # Panel must contain at least 6 unique qualified individuals
    assert panel_check["is_valid"] is True
    assert panel_check["unique_qualified_count"] == 6
    assert panel_check["linguists_count"] == 2
    assert panel_check["educators_count"] == 2
    assert panel_check["child_dev_count"] == 1
    assert panel_check["adjudicator_count"] == 1

    first_pass_count = panel_check["linguists_count"] + panel_check["educators_count"] + panel_check["child_dev_count"]
    assert first_pass_count == 5
    assert panel_check["adjudicator_count"] == 1
    assert first_pass_count + panel_check["adjudicator_count"] == 6

    # Verify project-team member is registered but isolated/excluded
    all_revs = registry.list_reviewers(qualified_only=False)
    team_members = [r for r in all_revs if r.is_project_team_member]
    assert len(team_members) == 1
    assert team_members[0].reviewer_id == "REV-S34-TEAM1"


def test_assignment_ledger_dual_competency_coverage():
    assert ASSIGNMENT_FILE.exists(), f"Missing assignment file: {ASSIGNMENT_FILE}"
    assignments = []
    with open(ASSIGNMENT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                assignments.append(json.loads(line))

    assert len(assignments) == 600

    # Group by item_id
    by_item = {}
    for a in assignments:
        by_item.setdefault(a["item_id"], []).append(a)

    assert len(by_item) == 150

    registry = setup_panel()
    panel_check = registry.verify_panel_composition()

    for item_id, item_assignments in by_item.items():
        # Exactly 4 assignments per item
        assert len(item_assignments) == 4, f"Item {item_id} does not have 4 assignments"

        # Unique reviewers per item
        rev_ids = [a["reviewer_id"] for a in item_assignments]
        assert len(set(rev_ids)) == 4, f"Duplicate reviewer assigned to item {item_id}"

        # Dual-competency checks
        linguists = [r for r in rev_ids if r in panel_check["linguist_ids"]]
        dev_raters = [r for r in rev_ids if r in panel_check["educator_ids"] or r in panel_check["child_dev_ids"]]

        assert len(linguists) >= 2, f"Item {item_id} has {len(linguists)} linguists (expected >= 2)"
        assert len(dev_raters) >= 2, f"Item {item_id} has {len(dev_raters)} developmental raters (expected >= 2)"
