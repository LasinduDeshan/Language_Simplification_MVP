"""Unit tests for the Stage 22 Label-Sufficiency Stop Condition Gate."""

import pytest
from app.complexity_analysis.label_auditor import LabelAuditor


def test_label_sufficiency_passes_when_all_classes_have_min_groups():
    auditor = LabelAuditor(min_folds_groups=3)
    records = []
    # 4 easy groups, 4 medium groups, 3 hard groups
    for i in range(4):
        records.append({"source_group_id": f"GRP-EASY-{i}", "assigned_difficulty": "easy", "label_status": "expert_verified"})
        records.append({"source_group_id": f"GRP-MED-{i}", "assigned_difficulty": "medium", "label_status": "reviewer_consensus"})
    for i in range(3):
        records.append({"source_group_id": f"GRP-HARD-{i}", "assigned_difficulty": "hard", "label_status": "expert_verified"})

    is_suff, max_folds, counts, msg = auditor.evaluate_label_sufficiency(records)
    assert is_suff
    assert max_folds == 3
    assert counts["hard"] == 3


def test_label_sufficiency_fails_when_one_class_has_insufficient_groups():
    auditor = LabelAuditor(min_folds_groups=3)
    records = []
    # 5 easy, 5 medium, but only 2 hard groups
    for i in range(5):
        records.append({"source_group_id": f"GRP-EASY-{i}", "assigned_difficulty": "easy", "label_status": "expert_verified"})
        records.append({"source_group_id": f"GRP-MED-{i}", "assigned_difficulty": "medium", "label_status": "expert_verified"})
    for i in range(2):
        records.append({"source_group_id": f"GRP-HARD-{i}", "assigned_difficulty": "hard", "label_status": "expert_verified"})

    is_suff, max_folds, counts, msg = auditor.evaluate_label_sufficiency(records)
    assert not is_suff
    assert max_folds == 2
    assert "Insufficient independently labeled groups for 3-fold CV" in msg


def test_provisional_labels_ignored_by_sufficiency_gate():
    auditor = LabelAuditor(min_folds_groups=3)
    records = []
    for i in range(5):
        records.append({"source_group_id": f"GRP-EASY-{i}", "assigned_difficulty": "easy", "label_status": "expert_verified"})
        records.append({"source_group_id": f"GRP-MED-{i}", "assigned_difficulty": "medium", "label_status": "expert_verified"})
    # Hard groups marked provisional only -> must NOT be promoted to Tier 1
    for i in range(5):
        records.append({"source_group_id": f"GRP-HARD-{i}", "assigned_difficulty": "hard", "label_status": "provisional"})

    is_suff, max_folds, counts, msg = auditor.evaluate_label_sufficiency(records)
    assert not is_suff
    assert counts["hard"] == 0
    assert "Missing class representation in Tier 1 labels" in msg
