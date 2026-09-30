"""
Unit tests for Stage 24 Protected Meaning Validator, Output Validator, and Schemas.
"""
import pytest
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    BaselineOutputRecord,
    BaselineConfiguration,
    FinalDisposition,
    MeaningValidationStatus,
    ProtectedElementSource,
)
from app.baseline_simplification.registry import BaselineRegistry
from app.baseline_simplification.protected_meaning_validator import ProtectedMeaningValidator
from app.baseline_simplification.output_validator import OutputValidator
import hashlib

def test_baseline_registry_export(tmp_path):
    reg = BaselineRegistry()
    methods = reg.list_methods()
    assert len(methods) == 6
    assert all(m.method_id in BaselineMethodId for m in methods)
    
    csv_path = tmp_path / "registry.csv"
    reg.export_to_csv(csv_path)
    assert csv_path.exists()
    content = csv_path.read_text(encoding="utf-8")
    assert "B0" in content
    assert "B4" in content
    assert "B5" in content

def test_protected_meaning_validator_entities_and_negation():
    validator = ProtectedMeaningValidator()
    
    # 1. Exact match should pass
    orig = "Alice and Bob did not visit Paris."
    simp = "Alice and Bob did not go to Paris."
    status, disp, violations = validator.validate(orig, simp)
    assert status == MeaningValidationStatus.PASSED
    assert disp == FinalDisposition.AUTOMATIC_CHECK_PASSED
    assert len(violations) == 0

    # 2. Negation drop should fail
    bad_simp = "Alice and Bob went to Paris."
    status, disp, violations = validator.validate(orig, bad_simp)
    assert status == MeaningValidationStatus.FAILED
    assert disp == FinalDisposition.AUTOMATIC_CHECK_FAILED
    assert any("Negation polarity" in v for v in violations)

    # 3. Missing quantity should fail
    orig_q = "She found 5 red apples."
    simp_q = "She found apples."
    status, disp, violations = validator.validate(orig_q, simp_q)
    assert status == MeaningValidationStatus.FAILED
    assert any("Missing numbers" in v for v in violations)

def test_output_validator_imperatives_and_fragments():
    validator = OutputValidator()
    
    # 1. Valid sentence
    valid, issues = validator.validate_text("The small dog barked loudly.")
    assert valid is True
    assert len(issues) == 0

    # 2. Short imperative with implied subject (allowed)
    valid_imp, issues_imp = validator.validate_text("Sit down.")
    assert valid_imp is True
    assert len(issues_imp) == 0

    valid_look, issues_look = validator.validate_text("Look here!")
    assert valid_look is True

    # 3. Fragment missing verb
    invalid, frag_issues = validator.validate_text("The big blue dog.")
    assert invalid is False
    assert any("Missing verb" in issue for issue in frag_issues)
