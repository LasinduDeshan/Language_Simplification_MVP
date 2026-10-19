"""
Stage 36 Dynamic Activity Localization & Token Contracts Tests
Verifies:
1. Schema contract validation for LocalizedText, LocalizedToken, LocalizedTargetSkill
2. Governed catalog lookup with UUID rejection constraint (Section 4.2)
3. validate_activity_localization availability reporting and token structure validation
4. Task, Attempt, and ChildSafeView enrichment for GRAM-WORD-001
"""
import pytest
from app.localization.activity_catalog import (
    GOVERNED_ACTIVITY_CATALOG,
    get_governed_activity_localization,
    validate_activity_localization,
    validate_token_structure,
    enrich_task_localization,
    enrich_attempt_localization,
    enrich_child_view_localization,
    is_uuid,
)
from app.schemas.schemas import (
    LocalizedText,
    LocalizedToken,
    LocalizedTargetSkill,
    TaskResponse,
    AttemptResponse,
    ChildSafeViewResponse,
)


def test_schema_contracts_localized_models():
    """Verify LocalizedText, LocalizedToken, and LocalizedTargetSkill schemas."""
    # LocalizedText
    lt = LocalizedText(en="The boy", si="පිරිමි ළමයා")
    assert lt.en == "The boy"
    assert lt.si == "පිරිමි ළමයා"

    # LocalizedToken
    tok = LocalizedToken(token_id="TOKEN-001", order=1, text=lt)
    assert tok.token_id == "TOKEN-001"
    assert tok.order == 1
    assert tok.text.si == "පිරිමි ළමයා"

    # LocalizedTargetSkill
    skill = LocalizedTargetSkill(
        code="WORD_ORDER_SVO",
        label=LocalizedText(en="S-V-O Word Order", si="කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ")
    )
    assert skill.code == "WORD_ORDER_SVO"
    assert skill.label.si == "කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ"


def test_governed_catalog_uuid_rejection():
    """Section 4.2: Catalogue lookup must reject attempt UUIDs and only resolve stable identifiers."""
    uuid_str = "17405b93-13bd-4a8a-9a1a-a0ee48164008"
    assert is_uuid(uuid_str) is True
    assert get_governed_activity_localization(uuid_str) is None

    # Stable task codes resolve cleanly
    gram_act = get_governed_activity_localization("GRAM-WORD-001")
    assert gram_act is not None
    assert gram_act["template_id"] == "GRAM-WORD-001"
    assert gram_act["title"]["si"] == "කර්තෘ–ක්‍රියා–කර්ම වාක්‍යය පෙළගස්වන්න"

    act_word = get_governed_activity_localization("ACT-WORD-001")
    assert act_word is not None
    assert act_word["task_code"] == "GRAM-WORD-001"


def test_validate_token_structure():
    """Validates structural integrity of localized tokens."""
    valid_token = {
        "token_id": "TOKEN-001",
        "order": 1,
        "text": {"en": "The boy", "si": "පිරිමි ළමයා"}
    }
    assert validate_token_structure(valid_token) is True

    # Missing token_id
    assert validate_token_structure({"order": 1, "text": {"en": "apple"}}) is False
    # Non-integer order
    assert validate_token_structure({"token_id": "T1", "order": "1", "text": {"en": "apple"}}) is False
    # Empty text map
    assert validate_token_structure({"token_id": "T1", "order": 1, "text": {"en": "", "si": "  "}}) is False


def test_validate_activity_localization_availability():
    """Verify validate_activity_localization correctly evaluates Sinhala completeness."""
    # GRAM-WORD-001 has full Sinhala authoring across title, instruction, tokens, skill
    gram_act = get_governed_activity_localization("GRAM-WORD-001")
    report = validate_activity_localization(gram_act, "si")
    assert report["requested_locale"] == "si"
    assert report["content_available"] is True
    assert len(report["missing_localized_fields"]) == 0

    # Incomplete activity: missing Sinhala token text
    incomplete_act = {
        "task_code": "CUSTOM-001",
        "title": {"en": "Ordering", "si": "පෙළගැස්වීම"},
        "instruction": {"en": "Order words", "si": "වචන පෙළගස්වන්න"},
        "target_skill": {"code": "WORD_ORDER", "label": {"en": "Order", "si": "පෙළගැස්වීම"}},
        "tokens": [
            {"token_id": "t1", "order": 1, "text": {"en": "boy", "si": ""}}
        ]
    }
    incomplete_report = validate_activity_localization(incomplete_act, "si")
    assert incomplete_report["content_available"] is False
    assert "tokens.t1.si" in incomplete_report["missing_localized_fields"]


def test_enrich_task_and_child_view_for_gram_word():
    """Verify task and child view enrichment with multilingual tokens and target skills."""
    raw_task = {
        "id": "task-uuid-gram-001",
        "task_code": "GRAM-WORD-001",
        "title": "Word Ordering: S-V-O Sentence",
        "original_instruction": "Put the words in the correct order."
    }

    enriched = enrich_task_localization(raw_task)
    assert enriched["title"]["si"] == "කර්තෘ–ක්‍රියා–කර්ම වාක්‍යය පෙළගස්වන්න"
    assert enriched["instruction"]["si"] == "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න."
    assert enriched["tokens"] is not None
    assert len(enriched["tokens"]) == 3
    assert enriched["tokens"][0]["text"]["si"] == "පිරිමි ළමයා"
    assert enriched["target_skill_details"]["code"] == "WORD_ORDER_SVO"
    assert enriched["content_language_status"]["si"] == "AVAILABLE"

    # Child safe view enrichment
    raw_child_view = {
        "presented_instruction": "Put the words in the correct order.",
        "supportive_message": "Good job!",
        "options": []
    }
    enriched_child = enrich_child_view_localization(raw_child_view, enriched, "si")
    assert enriched_child["tokens"] is not None
    assert len(enriched_child["tokens"]) == 3
    assert enriched_child["tokens"][0]["text"]["si"] == "පිරිමි ළමයා"
    assert enriched_child["tokens"][1]["text"]["si"] == "කැමතියි"
    assert enriched_child["tokens"][2]["text"]["si"] == "ඇපල්වලට"
    assert "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න" in enriched_child["presented_instruction_si"]
    assert "වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න" in enriched_child["instruction"]["si"]
    assert enriched_child["content_language_status"]["si"] == "AVAILABLE"
