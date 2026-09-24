"""Tests for common metadata and schema quality rules."""
import pytest
from app.datasets.quality.validators.common import CommonRecordValidator
from app.datasets.quality.enums import RuleSeverity


@pytest.fixture
def validator():
    return CommonRecordValidator()


def test_valid_common_record(validator):
    record = {
        "activity_id": "C3-EN-VOC-001",
        "schema_version": "1.0.0",
        "language": "en",
        "source": {"source_name": "Test Source"},
        "governance": {"validation_status": "draft"}
    }
    results = validator.validate(record)
    assert all(r.passed for r in results)


def test_invalid_schema_version_triggers_error(validator):
    record = {
        "activity_id": "C3-EN-VOC-002",
        "schema_version": "0.9.0",  # Invalid
        "language": "en"
    }
    results = validator.validate(record)
    schema_res = next(r for r in results if r.rule_id == "COMM-SCHEMA-001")
    assert schema_res.passed is False
    assert schema_res.severity == RuleSeverity.ERROR
