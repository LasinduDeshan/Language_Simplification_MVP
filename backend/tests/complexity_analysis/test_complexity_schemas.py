"""Unit tests for Stage 22 Pydantic schemas and data contracts."""

import pytest
from pydantic import ValidationError
from app.complexity_analysis.schemas import (
    ComplexityTrainingEligibility,
    ComplexityFactor,
    ComplexityClassificationResult,
    LabelAuditRecord,
    OODDetectionResult,
    ModelEvaluationSummary,
)


def test_complexity_factor_schema_valid():
    factor = ComplexityFactor(
        feature_name="avg_sentence_length",
        observed_value=14.5,
        contribution_direction="increases",
        importance=0.25,
        explanation_code="LONG_AVERAGE_SENTENCE",
    )
    assert factor.feature_name == "avg_sentence_length"
    assert factor.observed_value == 14.5


def test_complexity_factor_schema_extra_forbidden():
    with pytest.raises(ValidationError):
        ComplexityFactor(
            feature_name="avg_sentence_length",
            observed_value=14.5,
            contribution_direction="increases",
            explanation_code="LONG_AVERAGE_SENTENCE",
            extra_field="disallowed",  # type: ignore
        )


def test_classification_result_schema_valid():
    res = ComplexityClassificationResult(
        classification_id="CLS-TEST1234",
        text_instance_id="SRC-EN-001__SRC",
        source_group_id="SRC-EN-001",
        predicted_difficulty="easy",
        class_probabilities={"easy": 0.85, "medium": 0.10, "hard": 0.05},
        confidence=0.85,
        confidence_threshold=0.80,
        margin=0.75,
        margin_threshold=0.15,
        review_required=False,
        review_reasons=[],
        is_out_of_distribution=False,
        complexity_factors=[],
        model_name="Hist_Gradient_Boosting_Classifier",
        model_version="1.0.0",
        feature_schema_version="1.0.0",
        preprocessing_pipeline_version="1.0.0",
        source_dataset_version="0.2.0",
        record_hash="abcdef123456",
    )
    assert res.predicted_difficulty == "easy"
    assert not res.review_required


def test_label_audit_record_schema():
    rec = LabelAuditRecord(
        text_instance_id="SRC-001__SRC",
        parent_record_id="SRC-001",
        parent_record_type="source_item",
        source_group_id="SRC-001",
        assigned_difficulty="medium",
        label_status="expert_verified",
        annotator_tier="expert",
        provenance_source="expert_panel",
        rule_seeded_detected=False,
        circular_leakage_risk=False,
        audit_notes="Valid expert verification",
    )
    assert rec.label_status == "expert_verified"
    assert not rec.circular_leakage_risk
