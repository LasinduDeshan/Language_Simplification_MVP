"""9-step hierarchical mutually exclusive eligibility determination for Stage 22."""

from typing import Any, Dict, List
from app.complexity_analysis.schemas import (
    ComplexityTrainingEligibility,
    PrimaryDisposition,
    DatasetSplit,
    LabelStatus,
)


def determine_primary_disposition(
    dataset_split: str,
    parent_record_type: str,
    preprocessing_status: str,
    manual_review_required: bool,
    label_status: str,
) -> tuple[PrimaryDisposition, bool, bool, List[str]]:
    """Evaluates the strict 9-step hierarchical precedence order for a text instance.

    Returns:
        (primary_disposition, eligible_for_primary_training, eligible_for_secondary_experiment, exclusion_reasons)
    """
    reasons: List[str] = []

    # 1. locked_test
    if dataset_split == "development_candidate_test":
        reasons.append("Locked candidate test split quarantined")
        return "locked_test", False, False, reasons

    # 2. adaptation_test_excluded
    if parent_record_type == "adaptation_activity" or dataset_split == "adaptation_test":
        reasons.append("Adaptation activity parent / adaptation test set excluded from training")
        return "adaptation_test_excluded", False, False, reasons

    # 3. preprocessing_failed
    if preprocessing_status == "failed":
        reasons.append("NLP preprocessing failed")
        return "preprocessing_failed", False, False, reasons

    # 4. stage21_manual_review
    if manual_review_required:
        reasons.append("Stage 21 manual review required flag active")
        return "stage21_manual_review", False, False, reasons

    # 5. missing_or_conflicting_label
    if label_status in ("missing", "conflicting"):
        reasons.append(f"Label status is {label_status}")
        return "missing_or_conflicting_label", False, False, reasons

    # 6. provisional_secondary_only
    if label_status == "provisional":
        reasons.append("Provisional label status: eligible for secondary sensitivity experiment only")
        is_train = dataset_split == "development_candidate_train"
        return "provisional_secondary_only", False, is_train, reasons

    # 7. rule_seeded_audit_only
    if label_status == "rule_seeded":
        reasons.append("Rule-seeded label: eligible for circular leakage audit only")
        return "rule_seeded_audit_only", False, False, reasons

    # 8. primary_train_eligible
    if label_status in ("expert_verified", "reviewer_consensus"):
        if dataset_split == "development_candidate_train":
            return "primary_train_eligible", True, True, []
        elif dataset_split == "development_candidate_validation":
            return "primary_validation_eligible", False, False, []
        else:
            reasons.append(f"Unassigned or legacy split: {dataset_split}")
            return "missing_or_conflicting_label", False, False, reasons

    reasons.append(f"Unhandled condition: label_status={label_status}, split={dataset_split}")
    return "missing_or_conflicting_label", False, False, reasons


def evaluate_record_eligibility(
    record: Dict[str, Any],
    label_status: LabelStatus = "expert_verified",
    manual_review_required: bool = False,
) -> ComplexityTrainingEligibility:
    """Constructs a validated ComplexityTrainingEligibility contract for a given record."""
    text_instance_id = record["text_instance_id"]
    parent_record_id = record.get("parent_record_id", "")
    parent_record_type = record.get("parent_record_type", "source_item")
    text_role = record.get("text_role", "source_text")
    source_group_id = record.get("source_group_id", parent_record_id)
    dataset_split: DatasetSplit = record.get("dataset_split", "development_candidate_train")
    preprocessing_status = record.get("processing_status", "success")

    disposition, elig_train, elig_sec, reasons = determine_primary_disposition(
        dataset_split=dataset_split,
        parent_record_type=parent_record_type,
        preprocessing_status=preprocessing_status,
        manual_review_required=manual_review_required,
        label_status=label_status,
    )

    return ComplexityTrainingEligibility(
        text_instance_id=text_instance_id,
        parent_record_id=parent_record_id,
        parent_record_type=parent_record_type,
        text_role=text_role,
        source_group_id=source_group_id,
        dataset_split=dataset_split,
        preprocessing_status=preprocessing_status,
        label_status=label_status,
        primary_disposition=disposition,
        eligible_for_primary_training=elig_train,
        eligible_for_secondary_experiment=elig_sec,
        exclusion_reasons=reasons,
    )
