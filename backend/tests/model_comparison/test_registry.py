"""
Test system registry definitions and status for Stage 28A.
"""
import pytest
from app.model_comparison.registry import (
    SYSTEM_REGISTRY,
    get_registered_system,
    list_registered_systems,
    list_actively_evaluated_systems,
)
from app.model_comparison.schemas import (
    SystemEvaluationStatus,
    ExecutionCategory,
    GovernanceMetadata,
)


def test_registry_contains_all_systems():
    expected_ids = {"B0", "B1", "B2", "B3", "B4", "B5", "C1", "G1", "H1", "T1", "T2"}
    assert set(SYSTEM_REGISTRY.keys()) == expected_ids


def test_transformer_status_not_evaluated():
    t1 = get_registered_system("T1")
    t2 = get_registered_system("T2")

    assert t1 is not None
    assert t1.evaluation_status == SystemEvaluationStatus.NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS
    assert t1.is_active_candidate is False
    assert t1.execution_category == ExecutionCategory.LOCAL_TRANSFORMER

    assert t2 is not None
    assert t2.evaluation_status == SystemEvaluationStatus.NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS
    assert t2.is_active_candidate is False
    assert t2.execution_category == ExecutionCategory.LOCAL_TRANSFORMER


def test_actively_evaluated_systems_count():
    active = list_actively_evaluated_systems()
    # B0-B5 (6) + C1 (1) + G1 (1) + H1 (1) = 9 active systems
    assert len(active) == 9
    active_ids = {s.system_id for s in active}
    assert "T1" not in active_ids
    assert "T2" not in active_ids
    assert {"B0", "B1", "B2", "B3", "B4", "B5", "C1", "G1", "H1"}.issubset(active_ids)


def test_governance_metadata_defaults():
    gov = GovernanceMetadata()
    assert gov.evaluation_phase == "stage_28a_preliminary_automated_comparison"
    assert gov.expert_validated is False
    assert gov.approved_for_child_delivery is False
    assert gov.requires_expert_review is True
    assert gov.stage27_human_validation_status == "pending"
    assert gov.release_0_3_0_used is False
