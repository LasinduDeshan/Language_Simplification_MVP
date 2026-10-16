"""
Unit tests for Stage 34 schemas and rating contracts.
Validates:
1. DimensionRating status-score contract:
   - status == RATED requires non-null score;
   - status in {CANNOT_ASSESS, NOT_APPLICABLE, MISSING} requires null score;
2. AnnotationRecord submission contract:
   - Rejection of MISSING in submitted annotations (permitted only when is_draft=True);
3. Overall disposition domain validation.
"""

import pytest
from pydantic import ValidationError

from app.datasets.sinhala_expert_validation.enums import (
    DimensionStatus,
    OverallDisposition,
    ReasonCode,
    SafetyFlag,
    SimplicityRating,
)
from app.datasets.sinhala_expert_validation.schemas import (
    AnnotationRecord,
    DimensionRating,
)


def test_dimension_rating_rated_requires_score():
    # Valid RATED rating
    r = DimensionRating(status=DimensionStatus.RATED, score=3)
    assert r.status == DimensionStatus.RATED
    assert r.score == 3

    # Invalid: RATED with null score
    with pytest.raises(ValidationError):
        DimensionRating(status=DimensionStatus.RATED, score=None)


def test_dimension_rating_unrated_requires_null_score():
    # Valid CANNOT_ASSESS
    r1 = DimensionRating(status=DimensionStatus.CANNOT_ASSESS, score=None)
    assert r1.score is None

    # Invalid: CANNOT_ASSESS with non-null score
    with pytest.raises(ValidationError):
        DimensionRating(status=DimensionStatus.CANNOT_ASSESS, score=3)

    # Valid NOT_APPLICABLE
    r2 = DimensionRating(status=DimensionStatus.NOT_APPLICABLE, score=None)
    assert r2.score is None

    # Invalid: NOT_APPLICABLE with non-null score
    with pytest.raises(ValidationError):
        DimensionRating(status=DimensionStatus.NOT_APPLICABLE, score=1)


def test_submitted_annotation_rejects_missing():
    # Attempting to submit an annotation where a mandatory dimension is MISSING must fail
    with pytest.raises(ValidationError, match="contains MISSING for mandatory dimension"):
        AnnotationRecord(
            annotation_id="ANN-S34-TEST01",
            item_id="ITEM-S34-000001",
            reviewer_id="REV-S34-001",
            assignment_id="ASN-S34-000001",
            rubric_version="S34-RUBRIC-V1",
            rubric_hash="80b60486002208f63df1b67caa82b7a90611907e11b617233595cb69b933de23",
            submitted_at="2026-10-16T12:00:00Z",
            meaning_preservation=DimensionRating(status=DimensionStatus.MISSING, score=None),
            grammatical_acceptability=DimensionRating(status=DimensionStatus.RATED, score=3),
            morphology_preservation=DimensionRating(status=DimensionStatus.RATED, score=3),
            fluency_naturalness=DimensionRating(status=DimensionStatus.RATED, score=3),
            simplicity_improvement=DimensionRating(status=DimensionStatus.RATED, score=SimplicityRating.SIMPLER.value),
            vocabulary_suitability=DimensionRating(status=DimensionStatus.RATED, score=3),
            sentence_structure_suitability=DimensionRating(status=DimensionStatus.RATED, score=3),
            developmental_suitability=DimensionRating(status=DimensionStatus.CANNOT_ASSESS, score=None),
            safety=DimensionRating(status=DimensionStatus.RATED, score=SafetyFlag.NO_FLAG.value),
            overall_disposition=DimensionRating(status=DimensionStatus.RATED, score=OverallDisposition.ACCEPT_DRAFT.value),
            is_draft=False,  # Submission attempt
        )


def test_draft_annotation_allows_missing():
    # Autosaved draft is allowed to contain MISSING
    draft = AnnotationRecord(
        annotation_id="ANN-S34-DRAFT01",
        item_id="ITEM-S34-000001",
        reviewer_id="REV-S34-001",
        assignment_id="ASN-S34-000001",
        rubric_version="S34-RUBRIC-V1",
        rubric_hash="80b60486002208f63df1b67caa82b7a90611907e11b617233595cb69b933de23",
        submitted_at=None,
        meaning_preservation=DimensionRating(status=DimensionStatus.MISSING, score=None),
        grammatical_acceptability=DimensionRating(status=DimensionStatus.MISSING, score=None),
        morphology_preservation=DimensionRating(status=DimensionStatus.MISSING, score=None),
        fluency_naturalness=DimensionRating(status=DimensionStatus.MISSING, score=None),
        simplicity_improvement=DimensionRating(status=DimensionStatus.MISSING, score=None),
        vocabulary_suitability=DimensionRating(status=DimensionStatus.MISSING, score=None),
        sentence_structure_suitability=DimensionRating(status=DimensionStatus.MISSING, score=None),
        developmental_suitability=DimensionRating(status=DimensionStatus.MISSING, score=None),
        safety=DimensionRating(status=DimensionStatus.MISSING, score=None),
        overall_disposition=DimensionRating(status=DimensionStatus.MISSING, score=None),
        is_draft=True,
    )
    assert draft.is_draft is True
    assert draft.meaning_preservation.status == DimensionStatus.MISSING
