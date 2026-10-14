"""
Tests for Sinhala schema validations and default governance invariants.
"""
import pytest
from pydantic import ValidationError
from app.datasets.sinhala_foundation.schemas import SinhalaTechnicalFixture, LocalizedContentRecord

def test_sinhala_fixture_default_governance():
    fixture = SinhalaTechnicalFixture(
        fixture_id="FX-001",
        category="basic_sinhala",
        input_text="සිංහල",
        expected_code_points=["U+0D9A"],
        intended_test="code_point_preservation"
    )

    assert fixture.source_type == "technical_fixture"
    assert fixture.validation_status == "draft"
    assert fixture.research_eligible is False
    assert fixture.approved_for_child_delivery is False
    assert fixture.requires_expert_review is True

def test_extra_fields_forbidden_in_schemas():
    with pytest.raises(ValidationError):
        SinhalaTechnicalFixture(
            fixture_id="FX-002",
            category="basic",
            input_text="test",
            expected_code_points=[],
            intended_test="test",
            unauthorized_field="malicious"
        )
