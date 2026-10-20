"""
Unit and regression tests for Stage 36 Simplification Adapter.
Verifies multi-pass execution, discriminated Pydantic lineage, non-repetition of Attempt 2,
and strict immutability of Stage 33.
"""

import subprocess
import pytest
from app.localization.activity_catalog import GOVERNED_ACTIVITY_CATALOG
from app.localization.enums import TargetDisclosureClass, TargetDisclosurePolicy
from app.schemas.schemas import (
    ReuseLineage,
    RuleEngineLineage,
    SimplificationLineageResponse,
    TemplateLineage,
)
from app.sinhala_output_validation.simplification_adapter import Stage36SimplificationAdapter
from pydantic import TypeAdapter


def test_stage33_codebase_immutability():
    """Verify that Stage 33 directory has not been modified relative to stage-36-complete-v7."""
    cmd = ["git", "diff", "stage-36-complete-v7", "--", "backend/app/sinhala_simplification/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Git diff command failed: {result.stderr}"
    assert result.stdout.strip() == "", f"Stage 33 codebase was modified! Diff:\n{result.stdout}"


def test_adapter_template_fallback_produces_discriminated_lineage():
    """When Stage 33 candidate is rejected or unavailable, adapter uses validated catalog fallback."""
    adapter = Stage36SimplificationAdapter()

    res = adapter.simplify_attempt_3(
        task_code="VOC-NAMING-002",
        source_text="ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න.",
        attempt_2_instruction="තෝරන්න: පැන්සල හෝ පොත.",
        attempt_2_id="ATT-002",
        target_id="pencil",
        catalog_fallback_text="පින්තූර දෙස බලන්න. ලිවීමට භාවිත කරන දේ තෝරන්න.",
    )

    assert res["validation_passed"] is True
    assert res["presented_instruction"] == "පින්තූර දෙස බලන්න. ලිවීමට භාවිත කරන දේ තෝරන්න."
    assert res["presented_instruction"] != "තෝරන්න: පැන්සල හෝ පොත."

    lineage = res["lineage_dict"]
    assert lineage["generation_mode"] in ("RULE_ENGINE", "TEMPLATE_CATALOG")
    assert lineage["independent_performance_measure"] is False
    assert lineage["score_interpretation"] == "HIGHLY_SUPPORTED_PERFORMANCE"

    # Validate against Pydantic v2 discriminated union
    type_adapter = TypeAdapter(SimplificationLineageResponse)
    validated_model = type_adapter.validate_python(lineage)
    assert validated_model.generation_mode == lineage["generation_mode"]


def test_adapter_no_repetition_across_all_governed_activities():
    """Verifies that across all six governed activities, Attempt 3 never repeats Attempt 2."""
    adapter = Stage36SimplificationAdapter()

    for code, entry in GOVERNED_ACTIVITY_CATALOG.items():
        if code.startswith("ACT-") or code.startswith("TASK-00"):
            continue  # skip aliases

        source_si = entry["instruction"]["si"]
        att2_text = entry["support_versions"]["strong_scaffold"]["si"]
        att3_template = entry["support_versions"]["strong_decomposed_step"]["si"]
        target_id = entry.get("target_id")

        res = adapter.simplify_attempt_3(
            task_code=code,
            source_text=source_si,
            attempt_2_instruction=att2_text,
            attempt_2_id="ATT-002-MOCK",
            target_id=target_id,
            catalog_fallback_text=att3_template,
        )

        assert res["validation_passed"] is True
        # INVARIANT: Attempt 3 must not silently duplicate Attempt 2
        assert res["presented_instruction"] != att2_text, (
            f"Defect reproduced for activity {code}: Attempt 3 presented text "
            f"'{res['presented_instruction']}' matches Attempt 2 '{att2_text}'"
        )


def test_adapter_governed_reuse_when_minimal_reached():
    """When both Stage 33 and template fallback are unavailable, safe governed reuse is declared."""
    adapter = Stage36SimplificationAdapter()

    res = adapter.simplify_attempt_3(
        task_code="VOC-MATCH-001",
        source_text="පොතේ පින්තූරය සොයා තෝරන්න.",
        attempt_2_instruction="පොත සොයන්න.",
        attempt_2_id="ATT-002-VALID",
        target_id="book",
        catalog_fallback_text=None,  # No template fallback available
    )

    assert res["validation_passed"] is True
    lineage = res["lineage_dict"]
    assert lineage["generation_mode"] in ("RULE_ENGINE", "UNCHANGED_REUSE")
    if lineage["generation_mode"] == "UNCHANGED_REUSE":
        assert lineage["reused_from_attempt_id"] == "ATT-002-VALID"
        assert lineage["reuse_reason_code"] == "MINIMAL_SAFE_INSTRUCTION_ALREADY_REACHED"
