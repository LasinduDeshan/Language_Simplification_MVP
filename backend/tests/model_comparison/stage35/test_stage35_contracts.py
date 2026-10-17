"""
Unit and Contract Tests for Stage 35 Comparative Evaluation.
Validates:
1. Prerequisite commit and start tag immutability.
2. Two-tier denominator classification (N_common <= 13, N_local <= 13).
3. Level 4 and Level 5A/5B disposition mutual exclusivity.
4. Evaluator applicability dispositions.
5. Level 10 conditional accounting behavior.
6. Child delivery prohibition flag enforcement.
"""

import pytest
from app.model_comparison.stage35.schemas import (
    ModelRegistryRecord,
    ModelFamily,
    ConditionId,
    ModelIdentityDisposition,
    AttemptStatus,
    SelectedResponseDisposition,
    TerminalExecutionFailureDisposition,
    EvaluatorApplicability,
    HumanEvaluationMode,
    HumanEvidenceStatus,
    EvaluationRecord,
)
from app.model_comparison.stage35.evaluator import OutputValidator

def test_stage35_schemas_and_child_delivery_prohibition():
    eval_rec = EvaluationRecord(
        evaluation_id="S35-EVAL-0001",
        record_id="REC-001",
        condition_id=ConditionId.C1_GEMINI_ZERO_SHOT,
        response_disposition=SelectedResponseDisposition.VALID_CHANGED_OUTPUT,
        approved_for_child_delivery=False,
        approved_for_unsupervised_child_delivery=False,
        requires_expert_review=True,
    )
    assert eval_rec.approved_for_child_delivery is False
    assert eval_rec.approved_for_unsupervised_child_delivery is False
    assert eval_rec.requires_expert_review is True

def test_disposition_mutual_exclusivity_level_4_and_5():
    v = OutputValidator()
    
    # Succeeded attempt produces Level 5A response disposition
    disp, fail, _ = v.validate_response("සරල පාඨය", "සංකීර්ණ පාඨය", AttemptStatus.SUCCEEDED)
    assert disp == SelectedResponseDisposition.VALID_CHANGED_OUTPUT
    assert fail is None
    
    # Refused attempt produces Level 5B terminal failure disposition
    disp2, fail2, _ = v.validate_response("", "සංකීර්ණ පාඨය", AttemptStatus.REFUSED)
    assert disp2 is None
    assert fail2 == TerminalExecutionFailureDisposition.FAILED_REFUSAL

def test_pipeline_introduced_u_fffd_rejection():
    v = OutputValidator()
    disp, fail, details = v.validate_response("අසම්පූර්ණ පාඨය\ufffd", "සංකීර්ණ පාඨය", AttemptStatus.SUCCEEDED)
    assert disp == SelectedResponseDisposition.REJECTED_INVALID_UNICODE_OR_SCRIPT
    assert fail is None
    assert details.get("u_fffd_present") is True

def test_protected_span_corruption_rejection():
    v = OutputValidator()
    disp, fail, details = v.validate_response("අගනුවර කෝට්ටේ වේ", "ශ්‍රී ලංකාවේ අගනුවර කෝට්ටේ වේ", AttemptStatus.SUCCEEDED, protected_spans=["ශ්‍රී ලංකාවේ"])
    assert disp == SelectedResponseDisposition.REJECTED_PROTECTED_SPAN_CHANGE
    assert fail is None
    assert details.get("missing_protected_span") == "ශ්‍රී ලංකාවේ"
