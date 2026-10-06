"""
Tests for Stage 26 Governance Invariants, Group-Safe Eligibility, Corpus Immutability, and Decision Gates.
"""
from pathlib import Path
from app.model_simplification.training.eligibility import (
    GroupSafeEligibilityAuditor,
    ALL_DISPOSITIONS,
    DISPOSITION_ELIGIBLE_INTERNAL_TRAINING,
)
from app.model_simplification.training.dataset_builder import Seq2SeqDatasetBuilder
from app.model_simplification.registry import ModelRegistry


def test_recalculated_contaminated_groups():
    auditor = GroupSafeEligibilityAuditor()
    result = auditor.run_audit()
    rec = result["reconciliation"]
    
    # Verify exact accounting counts
    assert rec["total_pairs"] == 900
    assert rec["total_groups"] == 300
    assert rec["directly_flagged_reformulation_pairs"] == 326
    assert rec["dynamically_recalculated_contaminated_groups"] == 203
    assert rec["total_group_reformulation_excluded_pairs"] == 609
    assert rec["eligible_internal_training_groups"] == 70
    assert rec["eligible_internal_training_pairs"] == 210
    assert rec["mutually_exclusive_sum"] == 900


def test_complete_three_tier_group_requirement():
    auditor = GroupSafeEligibilityAuditor()
    result = auditor.run_audit()
    manifest_groups = result.get("eligible_groups", [])
    assert len(manifest_groups) == 70
    for g in manifest_groups:
        assert g["source_record_modified"] is False


def test_stage25_comparator_hash_immutability():
    registry = ModelRegistry()
    s25 = registry.get("stage25-controlled-deterministic")
    assert s25 is not None
    assert s25.commit_revision == "6b785502b860d4e93d2d31b86bd653c33a210ac9"
    assert s25.config_hash is not None
