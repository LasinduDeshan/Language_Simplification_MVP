"""
Tests for Governed Sinhala Subject and Predicate Grammar Task (GRAM-SI-SUBPRED-001)

Verifies:
1. Catalogue resolution by task_code and alias template_id.
2. Attempt UUID rejection for catalogue resolution.
3. Governance & safety invariant verification (draft, child delivery unapproved).
4. Unicode NFC normalization of all Sinhala strings.
5. Linguistic structure: Predicate includes verb and associated words; verb is not whole predicate.
6. Answer evaluation via answer_checker:
   - Correct subject and predicate -> target_skill_result='correct', retry_required=False
   - Subject only -> partial result
   - Predicate only -> partial result
   - Verb-only as predicate -> triggers 'predicate_incomplete_verb_only' observation
7. Activity localization completeness validation (fail-closed check).
8. Attempt progression and strategy mapping.
"""
from types import SimpleNamespace
import unicodedata
import pytest
from app.localization.activity_catalog import (
    get_governed_activity_localization,
    validate_activity_localization,
    is_uuid,
)
from app.response_analysis.answer_checker import answer_checker, normalize_nfc
from app.localization.enums import GovernedTaskType


def test_catalog_resolution():
    """Verify GRAM-SI-SUBPRED-001 resolves by canonical code and legacy alias."""
    task = get_governed_activity_localization("GRAM-SI-SUBPRED-001")
    assert task is not None
    assert task["task_code"] == "GRAM-SI-SUBPRED-001"
    assert task["template_id"] == "GRAM-SI-SUBPRED-001"
    assert task["task_type"] == GovernedTaskType.SUBJECT_PREDICATE_IDENTIFICATION

    # Alias check
    alias_task = get_governed_activity_localization("ACT-SUBPRED-001")
    assert alias_task is not None
    assert alias_task["task_code"] == "GRAM-SI-SUBPRED-001"


def test_catalog_uuid_rejection():
    """Verify attempt UUIDs are rejected as catalogue keys."""
    uuid_str = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
    assert is_uuid(uuid_str) is True
    assert get_governed_activity_localization(uuid_str) is None


def test_governance_safety_invariants():
    """Verify all child safety and governance flags are strictly locked."""
    task = get_governed_activity_localization("GRAM-SI-SUBPRED-001")
    assert task is not None
    assert task["validation_status"] == "draft"
    assert task["expert_validated"] is False
    assert task["research_eligible"] is False
    assert task["approved_for_child_delivery"] is False
    assert task["approved_for_unsupervised_child_delivery"] is False
    assert task["requires_expert_review"] is True


def test_unicode_nfc_normalization():
    """Verify all Sinhala text in the catalogue record is NFC-normalized."""
    task = get_governed_activity_localization("GRAM-SI-SUBPRED-001")
    assert task is not None

    def assert_nfc(val):
        if isinstance(val, str):
            assert val == unicodedata.normalize("NFC", val), f"String not NFC normalized: {val}"
        elif isinstance(val, dict):
            for v in val.values():
                assert_nfc(v)
        elif isinstance(val, list):
            for item in val:
                assert_nfc(item)

    assert_nfc(task["title"])
    assert_nfc(task["instruction"])
    assert_nfc(task["learning_objective"])
    assert_nfc(task["support_versions"])
    assert_nfc(task["feedback_copy"])
    for item in task["items"]:
        assert_nfc(item)


def test_linguistic_structure_predicate_not_just_verb():
    """Verify each governed example has subject, predicate, and verb where verb is within predicate but not identical."""
    task = get_governed_activity_localization("GRAM-SI-SUBPRED-001")
    assert task is not None
    assert len(task["items"]) >= 5

    for item in task["items"]:
        sentence = item["sentence"]
        subject = item["subject"]
        predicate = item["predicate"]
        verb = item["verb"]

        assert subject in sentence, f"Subject '{subject}' not in '{sentence}'"
        assert predicate in sentence, f"Predicate '{predicate}' not in '{sentence}'"
        assert verb in predicate, f"Verb '{verb}' must be contained within predicate '{predicate}'"
        # The core linguistic rule: ආඛ්‍යාතය is not ONLY the verb
        assert predicate != verb, f"Predicate '{predicate}' should not be defined as only the verb '{verb}'"
        assert len(predicate) > len(verb), "Predicate should contain other words besides the verb in these examples"


def test_validate_activity_localization_completeness():
    """Verify activity passes fail-closed Sinhala availability checks with 0 missing fields."""
    task = get_governed_activity_localization("GRAM-SI-SUBPRED-001")
    report = validate_activity_localization(task, "si")
    assert report["requested_locale"] == "si"
    assert report["content_available"] is True
    assert len(report["missing_localized_fields"]) == 0


def test_answer_evaluation_correct():
    """Verify answer evaluation produces full credit when both subject and predicate are correct."""
    task_mock = SimpleNamespace(
        task_code="GRAM-SI-SUBPRED-001",
        task_type="SUBJECT_PREDICATE_IDENTIFICATION",
        target_skill="subject_predicate_identification",
        expected_concepts=["ළමයා", "පොත කියවයි"],
        acceptable_answers=["ළමයා පොත කියවයි."],
        grammar_targets=["subject_predicate_identification"],
    )

    user_response = {
        "subject": "ළමයා",
        "predicate": "පොත කියවයි"
    }

    result = answer_checker.evaluate_answer(
        task_mock,
        transcript="",
        selected_answer=user_response
    )

    assert result["concept_result"] == "correct"
    assert result["target_skill_result"] == "correct"
    assert result["retry_required"] is False
    assert "subject_identified" in result["grammar_observations"]
    assert "predicate_identified" in result["grammar_observations"]
    assert "predicate_incomplete_verb_only" not in result["grammar_observations"]


def test_answer_evaluation_verb_only_pedagogical_trap():
    """Verify selecting only the verb as the predicate triggers the specific pedagogical flag."""
    task_mock = SimpleNamespace(
        task_code="GRAM-SI-SUBPRED-001",
        task_type="SUBJECT_PREDICATE_IDENTIFICATION",
        target_skill="subject_predicate_identification",
        expected_concepts=["ළමයා", "පොත කියවයි"],
        acceptable_answers=["ළමයා පොත කියවයි."],
        grammar_targets=["subject_predicate_identification"],
    )

    user_response = {
        "subject": "ළමයා",
        "predicate": "කියවයි"  # Only the verb!
    }

    result = answer_checker.evaluate_answer(
        task_mock,
        transcript="",
        selected_answer=user_response
    )

    assert result["concept_result"] == "partial"
    assert result["target_skill_result"] == "partial"
    assert result["retry_required"] is True
    assert "subject_identified" in result["grammar_observations"]
    assert "predicate_incomplete_verb_only" in result["grammar_observations"]
    assert "predicate_identified" not in result["grammar_observations"]


def test_answer_evaluation_partial_subject_only():
    """Verify partial correctness when only subject is provided/correct."""
    task_mock = SimpleNamespace(
        task_code="GRAM-SI-SUBPRED-001",
        task_type="SUBJECT_PREDICATE_IDENTIFICATION",
        target_skill="subject_predicate_identification",
        expected_concepts=["ළමයා", "පොත කියවයි"],
        acceptable_answers=["ළමයා පොත කියවයි."],
        grammar_targets=["subject_predicate_identification"],
    )

    user_response = {
        "subject": "ළමයා",
        "predicate": ""
    }

    result = answer_checker.evaluate_answer(
        task_mock,
        transcript="",
        selected_answer=user_response
    )

    assert result["concept_result"] == "partial"
    assert result["target_skill_result"] == "partial"
    assert result["retry_required"] is True
    assert "subject_identified" in result["grammar_observations"]
    assert "predicate_missing_or_incomplete" in result["grammar_observations"]


def test_answer_evaluation_partial_predicate_only():
    """Verify partial correctness when only predicate is provided/correct."""
    task_mock = SimpleNamespace(
        task_code="GRAM-SI-SUBPRED-001",
        task_type="SUBJECT_PREDICATE_IDENTIFICATION",
        target_skill="subject_predicate_identification",
        expected_concepts=["ළමයා", "පොත කියවයි"],
        acceptable_answers=["ළමයා පොත කියවයි."],
        grammar_targets=["subject_predicate_identification"],
    )

    user_response = {
        "subject": "වැරදි_උක්තය",
        "predicate": "පොත කියවයි"
    }

    result = answer_checker.evaluate_answer(
        task_mock,
        transcript="",
        selected_answer=user_response
    )

    assert result["concept_result"] == "partial"
    assert result["target_skill_result"] == "partial"
    assert result["retry_required"] is True
    assert "predicate_identified" in result["grammar_observations"]
    assert "subject_missing" in result["grammar_observations"]


def test_enrich_task_localization_subpred():
    """Verify enrich_task_localization dynamically binds tokens and Sinhala metadata."""
    from app.localization.activity_catalog import enrich_task_localization, enrich_child_view_localization
    raw_task = {
        "id": "task-uuid-subpred",
        "task_code": "GRAM-SI-SUBPRED-001",
        "title": "Identifying the Subject and Predicate",
        "original_instruction": "Identify the subject and predicate in the sentence."
    }
    enriched = enrich_task_localization(raw_task)
    assert enriched["title"]["si"] == "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම"
    assert enriched["instruction"]["si"] == "වාක්‍යයේ උක්තය සහ ආඛ්‍යාතය හඳුනාගන්න."
    assert enriched["tokens"] is not None
    assert len(enriched["tokens"]) == 3
    assert enriched["tokens"][0]["text"]["si"] == "ළමයා"
    assert enriched["tokens"][1]["text"]["si"] == "පොත"
    assert enriched["tokens"][2]["text"]["si"] == "කියවයි"
    assert enriched["target_skill_details"]["code"] == "SUBJECT_PREDICATE_IDENTIFICATION"
    assert enriched["content_language_status"]["si"] == "AVAILABLE"

    # Child view enrichment
    raw_child_view = {
        "presented_instruction": "Identify the subject and predicate.",
        "supportive_message": "Good job!",
        "options": []
    }
    enriched_child = enrich_child_view_localization(raw_child_view, enriched, "si")
    assert enriched_child["tokens"] is not None
    assert len(enriched_child["tokens"]) == 3
    assert "පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න." in enriched_child["presented_instruction_si"]
    assert enriched_child["instruction"]["si"] == "පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න."
    assert enriched_child["content_language_status"]["si"] == "AVAILABLE"


def test_api_activities_includes_governed_subpred():
    """Verify get_activities synthesizes and includes GRAM-SI-SUBPRED-001 with Sinhala fields."""
    from unittest.mock import MagicMock
    from app.api.routes import get_activities

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    activities = get_activities(category=None, subskill=None, age=None, delivery_mode=None, db=mock_db)
    subpred = next((a for a in activities if (a.get("task_code") if isinstance(a, dict) else getattr(a, "task_code", None)) == "GRAM-SI-SUBPRED-001"), None)
    assert subpred is not None
    title_si = subpred.get("title_si") if isinstance(subpred, dict) else getattr(subpred, "title_si", None)
    assert title_si == "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම"
    title = subpred.get("title") if isinstance(subpred, dict) else getattr(subpred, "title", None)
    assert (title.get("en") if isinstance(title, dict) else getattr(title, "en", None)) == "Identifying the Subject and Predicate"
    ar_meta = subpred.get("ar_metadata") if isinstance(subpred, dict) else getattr(subpred, "ar_metadata", {})
    assert ar_meta.get("approved_for_child_delivery") is False
    assert ar_meta.get("validation_status") == "draft"


def test_api_activity_detail_subpred():
    """Verify get_activity retrieves full synthesized task detail."""
    from unittest.mock import MagicMock
    from app.api.routes import get_activity

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    data = get_activity("GRAM-SI-SUBPRED-001", db=mock_db)
    task_code = data.get("task_code") if isinstance(data, dict) else getattr(data, "task_code", None)
    assert task_code == "GRAM-SI-SUBPRED-001"
    title_si = data.get("title_si") if isinstance(data, dict) else getattr(data, "title_si", None)
    assert title_si == "උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම"
    instruction_si = data.get("instruction_si") if isinstance(data, dict) else getattr(data, "instruction_si", None)
    assert instruction_si == "වාක්‍යයේ උක්තය සහ ආඛ්‍යාතය හඳුනාගන්න."
    ar_meta = data.get("ar_metadata") if isinstance(data, dict) else getattr(data, "ar_metadata", {})
    assert ar_meta.get("approved_for_child_delivery") is False
    assert ar_meta.get("validation_status") == "draft"

