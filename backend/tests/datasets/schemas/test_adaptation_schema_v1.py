import pytest
from app.datasets.adaptation_test_set.schemas import AdaptationRecordV1, ProtectedElements
from app.datasets.common.enums import (
    LanguageCode, ActivityOwner, PrimaryDomain, DifficultyLevel, AdaptationPolicy
)

def test_valid_adaptation_record():
    rec = AdaptationRecordV1(
        activity_id="C3-EN-VOC-0001",
        activity_owner=ActivityOwner.COMPONENT_3_LANGUAGE,
        language=LanguageCode.EN,
        activity_type="naming",
        primary_domain=PrimaryDomain.VOCABULARY,
        age_min=4,
        age_max=6,
        difficulty=DifficultyLevel.EASY,
        original_instruction="Name the pictured object.",
        protected=ProtectedElements(answer="apple", elements=["apple"])
    )
    assert rec.activity_id == "C3-EN-VOC-0001"
    assert rec.schema_version == "1.0.0"
    assert rec.dataset_version == "0.1.0"

def test_invalid_age_bounds():
    with pytest.raises(ValueError, match="age_min .* cannot exceed age_max"):
        AdaptationRecordV1(
            activity_id="C3-EN-VOC-0001",
            primary_domain=PrimaryDomain.VOCABULARY,
            age_min=7,
            age_max=5,
            original_instruction="Test"
        )

def test_extra_fields_forbidden():
    with pytest.raises(Exception):
        AdaptationRecordV1(
            activity_id="C3-EN-VOC-0001",
            primary_domain=PrimaryDomain.VOCABULARY,
            original_instruction="Test",
            unexpected_field="disallowed"
        )
