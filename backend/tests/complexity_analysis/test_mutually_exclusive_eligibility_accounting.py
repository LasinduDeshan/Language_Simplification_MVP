"""Unit tests for the 9-step hierarchical mutually exclusive eligibility precedence."""

import pytest
from app.complexity_analysis.eligibility import (
    determine_primary_disposition,
    evaluate_record_eligibility,
)


def test_locked_test_takes_highest_precedence():
    # Locked test should override even if label is missing or provisional or failed
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_test",
        parent_record_type="source_item",
        preprocessing_status="failed",
        manual_review_required=True,
        label_status="missing",
    )
    assert disp == "locked_test"
    assert not train_elig
    assert not sec_elig


def test_adaptation_test_excluded_precedence():
    # Adaptation activity overrides missing label or review flag
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="adaptation_test",
        parent_record_type="adaptation_activity",
        preprocessing_status="success",
        manual_review_required=True,
        label_status="expert_verified",
    )
    assert disp == "adaptation_test_excluded"
    assert not train_elig


def test_preprocessing_failed_precedence():
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="failed",
        manual_review_required=False,
        label_status="expert_verified",
    )
    assert disp == "preprocessing_failed"
    assert not train_elig


def test_stage21_manual_review_precedence():
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=True,
        label_status="expert_verified",
    )
    assert disp == "stage21_manual_review"
    assert not train_elig


def test_missing_or_conflicting_label_precedence():
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=False,
        label_status="missing",
    )
    assert disp == "missing_or_conflicting_label"
    assert not train_elig


def test_provisional_secondary_only_precedence():
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=False,
        label_status="provisional",
    )
    assert disp == "provisional_secondary_only"
    assert not train_elig
    assert sec_elig  # eligible for secondary experiment


def test_rule_seeded_audit_only_precedence():
    disp, train_elig, sec_elig, reasons = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=False,
        label_status="rule_seeded",
    )
    assert disp == "rule_seeded_audit_only"
    assert not train_elig
    assert not sec_elig


def test_primary_train_and_validation_eligibility():
    disp_train, train_elig, sec_elig, _ = determine_primary_disposition(
        dataset_split="development_candidate_train",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=False,
        label_status="expert_verified",
    )
    assert disp_train == "primary_train_eligible"
    assert train_elig
    assert sec_elig

    disp_val, val_train_elig, val_sec_elig, _ = determine_primary_disposition(
        dataset_split="development_candidate_validation",
        parent_record_type="source_item",
        preprocessing_status="success",
        manual_review_required=False,
        label_status="reviewer_consensus",
    )
    assert disp_val == "primary_validation_eligible"
    assert not val_train_elig
