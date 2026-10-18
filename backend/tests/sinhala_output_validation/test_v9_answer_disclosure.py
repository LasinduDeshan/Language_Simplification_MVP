"""
Unit and regression tests for Stage 36 Validator V9: Answer Disclosure Gate & Decomposed Step Complexity.
Tests grapheme-safe token matching, Sinhala inflections, explicit task target vs inferred answer policies,
and per-step complexity bounds.
"""

import pytest
from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy
from app.sinhala_output_validation.schemas import (
    CandidateEnvelope,
    ExecutionMode,
    SeverityLevel,
)
from app.sinhala_output_validation.validators.v9_answer_disclosure import ValidatorV9AnswerDisclosureGate


def _build_dummy_envelope() -> CandidateEnvelope:
    return CandidateEnvelope(
        candidate_id="CAND-TEST-V9-001",
        request_id="REQ-TEST-V9-001",
        source_record_id="TASK-VOC-TEST",
        source_text_ref="governed://task/test/source",
        source_text_sha256_internal="a" * 64,
        candidate_text_ref="governed://task/test/cand",
        candidate_text_sha256_internal="b" * 64,
        execution_mode=ExecutionMode.RULE_ENGINE,
        generation_configuration_hash="test_config_hash_v1",
    )


def test_v9_may_repeat_task_target_policy_allows_target():
    """Directive tasks like Book Finder or Shape Match allow repeating task targets."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-MATCH-001",
        "target_id": "book",
        "target_disclosure_class": TargetDisclosureClass.EXPLICIT_TASK_TARGET,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
        "target_aliases": {
            "si": ["පොත", "පොතට", "පොතෙන්"],
            "en": ["book"]
        }
    }

    source_text = "පොතේ පින්තූරය සොයා තෝරන්න."
    candidate_text = "පින්තූර දෙක බලන්න. පොතේ පින්තූරය තෝරන්න."

    findings = v9.validate(source_text, candidate_text, env, context)
    disclosure_findings = [f for f in findings if f.reason_code == "REJ_ANSWER_DISCLOSURE_DETECTED"]
    assert len(disclosure_findings) == 0


def test_v9_do_not_reveal_policy_detects_base_target():
    """Inference tasks prohibit naming the target item."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-NAMING-002",
        "target_id": "pencil",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "target_aliases": {
            "si": ["පැන්සල", "පැන්සලට", "පැන්සලෙන්", "පැන්සල්"],
            "en": ["pencil"]
        }
    }

    source_text = "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
    candidate_revealing = "තෝරන්න: පැන්සල හෝ පොත."

    findings = v9.validate(source_text, candidate_revealing, env, context)
    disclosure_findings = [f for f in findings if f.reason_code == "REJ_ANSWER_DISCLOSURE_DETECTED"]
    assert len(disclosure_findings) == 1
    assert disclosure_findings[0].severity == SeverityLevel.CRITICAL
    # Verify public summary does not leak the plaintext target
    assert "පැන්සල" not in disclosure_findings[0].public_summary


@pytest.mark.parametrize("inflected_text, target_id, target_si_stem", [
    ("පැන්සල ගන්න.", "pencil", "පැන්සල"),
    ("මෙම පැන්සලට තට්ටු කරන්න.", "pencil", "පැන්සල"),
    ("පැන්සලෙන් ලියන්න.", "pencil", "පැන්සල"),
    ("පැන්සලක් තෝරන්න.", "pencil", "පැන්සල"),
    ("පූසාගේ රූපය බලන්න.", "cat", "පූසා"),
    ("පොතෙන් එකක් ගන්න.", "book", "පොත"),
])
def test_v9_detects_sinhala_inflections(inflected_text, target_id, target_si_stem):
    """Verifies that conservative Sinhala inflections (dative, ablative, genitive, indefinite) are detected."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-TEST-INFLECT",
        "target_id": target_id,
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "target_aliases": {
            "si": [target_si_stem],
            "en": [target_id]
        }
    }

    findings = v9.validate("මූලික උපදෙස.", inflected_text, env, context)
    disclosure_findings = [f for f in findings if f.reason_code == "REJ_ANSWER_DISCLOSURE_DETECTED"]
    assert len(disclosure_findings) >= 1
    assert disclosure_findings[0].severity == SeverityLevel.CRITICAL


def test_v9_non_revealing_decomposition_passes():
    """Non-revealing action guidance instructions must pass V9 without disclosure violations."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-NAMING-002",
        "target_id": "pencil",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "target_aliases": {
            "si": ["පැන්සල", "පැන්සලට", "පැන්සලෙන්"],
            "en": ["pencil"]
        },
        "strategy_code": "STRONG_DECOMPOSED_STEP",
        "attempt_number": 3,
    }

    source_text = "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
    candidate_safe = "පින්තූර දෙක බලන්න. ලිවීමට භාවිත කරන දේ තෝරන්න."

    findings = v9.validate(source_text, candidate_safe, env, context)
    critical_findings = [f for f in findings if f.severity == SeverityLevel.CRITICAL]
    assert len(critical_findings) == 0


def test_v9_rejects_grapheme_substring_overlap_false_positives():
    """Words sharing letters with target aliases but having different meanings must NOT trigger false positives."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-NAMING-002",
        "target_id": "pencil",
        "target_disclosure_class": TargetDisclosureClass.INFERRED_ANSWER,
        "target_disclosure_policy": TargetDisclosurePolicy.DO_NOT_REVEAL,
        "target_aliases": {
            "si": ["පැන්සල", "පැන්සලට", "පැන්සලෙන්"],
            "en": ["pencil"]
        }
    }

    # "සැපපහසු" and "පැලැස්තර" should not trigger a match for "පැන්සල"
    source_text = "ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න."
    candidate_non_match = "සැපපහසු ස්ථානයක් බලන්න. රූපය තෝරන්න."

    findings = v9.validate(source_text, candidate_non_match, env, context)
    disclosure_findings = [f for f in findings if f.reason_code == "REJ_ANSWER_DISCLOSURE_DETECTED"]
    assert len(disclosure_findings) == 0


def test_v9_per_step_complexity_bounds():
    """Decomposed instructions must not exceed 2 sub-steps or 8 words per sub-step."""
    v9 = ValidatorV9AnswerDisclosureGate()
    env = _build_dummy_envelope()

    context = {
        "task_id": "VOC-NAMING-002",
        "strategy_code": "STRONG_DECOMPOSED_STEP",
        "attempt_number": 3,
        "target_disclosure_policy": TargetDisclosurePolicy.MAY_REPEAT_TASK_TARGET,
    }

    # Test > 2 steps
    three_step_text = "පළමුව බලන්න. දෙවනුව හිතන්න. තුන්වනුව තෝරන්න."
    findings_3steps = v9.validate("මූලික.", three_step_text, env, context)
    too_many_steps = [f for f in findings_3steps if f.reason_code == "DIAG_DECOMPOSED_TOO_MANY_STEPS"]
    assert len(too_many_steps) == 1

    # Test > 8 words in one step
    long_step_text = "මෙම පින්තූරය ඉතාම හොඳින් හා නිවැරදිව පරීක්ෂා කර බලා වඩාත් නිවැරදි පිළිතුර තෝරන්න."
    findings_long = v9.validate("මූලික.", long_step_text, env, context)
    word_limit = [f for f in findings_long if f.reason_code == "DIAG_DECOMPOSED_STEP_WORD_LIMIT_EXCEEDED"]
    assert len(word_limit) == 1
