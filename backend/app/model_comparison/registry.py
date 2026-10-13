"""
System Registry for Stage 28A Preliminary English Model Comparison.
Defines registered systems B0-H1 and T1-T2 with execution and evaluation status.
"""
from typing import Dict, List, Optional
from app.model_comparison.schemas import (
    RegisteredSystem,
    ExecutionCategory,
    SystemEvaluationStatus,
)


SYSTEM_REGISTRY: Dict[str, RegisteredSystem] = {
    "B0": RegisteredSystem(
        system_id="B0",
        name="Identity Baseline",
        execution_category=ExecutionCategory.DETERMINISTIC_REFERENCE,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="identity",
        is_active_candidate=True,
        notes="Unmodified source text used as lower-bound baseline",
    ),
    "B1": RegisteredSystem(
        system_id="B1",
        name="Lexical Substitution Baseline",
        execution_category=ExecutionCategory.DETERMINISTIC_BASELINE,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage24_lexical_substitution",
        is_active_candidate=True,
        notes="Frozen Stage 24 lexical substitution rules",
    ),
    "B2": RegisteredSystem(
        system_id="B2",
        name="Sentence Splitting Baseline",
        execution_category=ExecutionCategory.DETERMINISTIC_BASELINE,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage24_sentence_splitting",
        is_active_candidate=True,
        notes="Frozen Stage 24 sentence splitting heuristic",
    ),
    "B3": RegisteredSystem(
        system_id="B3",
        name="Syntactic Rules Baseline",
        execution_category=ExecutionCategory.DETERMINISTIC_BASELINE,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage24_syntactic_rules",
        is_active_candidate=True,
        notes="Frozen Stage 24 syntax simplification transformations",
    ),
    "B4": RegisteredSystem(
        system_id="B4",
        name="Combined Deterministic Baseline",
        execution_category=ExecutionCategory.DETERMINISTIC_BASELINE,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage24_combined_baseline",
        is_active_candidate=True,
        notes="Frozen Stage 24 multi-heuristic baseline (lexical + split + syntax)",
    ),
    "B5": RegisteredSystem(
        system_id="B5",
        name="Offline Deterministic Fallback",
        execution_category=ExecutionCategory.DETERMINISTIC_FALLBACK,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage25_deterministic_fallback",
        is_active_candidate=True,
        notes="Stage 25 offline fallback pipeline evaluated under independent attribution",
    ),
    "C1": RegisteredSystem(
        system_id="C1",
        name="Stage 25 Controlled Engine",
        execution_category=ExecutionCategory.CONTROLLED_RULES,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="stage25_controlled_engine",
        is_active_candidate=True,
        notes="Controlled simplification engine from stage-25-complete-v2",
    ),
    "G1": RegisteredSystem(
        system_id="G1",
        name="Gemini Native Simplification",
        execution_category=ExecutionCategory.LIVE_EXTERNAL_LLM,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="gemini-3.5-flash-lite",
        is_active_candidate=True,
        notes="Live Gemini generation; evaluated on native outputs only (no fallback substitution)",
    ),
    "H1": RegisteredSystem(
        system_id="H1",
        name="Stage 26 Governed Hybrid Pipeline",
        execution_category=ExecutionCategory.GOVERNED_HYBRID,
        evaluation_status=SystemEvaluationStatus.REGISTERED_AND_EVALUATED,
        model_identifier="gemini_plus_stage25_hybrid",
        is_active_candidate=True,
        notes="Gemini native + Stage 25 deterministic repair & fallback safety governance",
    ),
    "T1": RegisteredSystem(
        system_id="T1",
        name="mT5 Native Simplification",
        execution_category=ExecutionCategory.LOCAL_TRANSFORMER,
        evaluation_status=SystemEvaluationStatus.NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS,
        model_identifier="google/mt5-small",
        is_active_candidate=False,
        notes="Local transformer; registered but not evaluated if local checkpoint produces 0 native outputs",
    ),
    "T2": RegisteredSystem(
        system_id="T2",
        name="mBART Native Simplification",
        execution_category=ExecutionCategory.LOCAL_TRANSFORMER,
        evaluation_status=SystemEvaluationStatus.NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS,
        model_identifier="facebook/mbart-large-50",
        is_active_candidate=False,
        notes="Local transformer; registered but not evaluated if local checkpoint produces 0 native outputs",
    ),
}


def get_registered_system(system_id: str) -> Optional[RegisteredSystem]:
    return SYSTEM_REGISTRY.get(system_id)


def list_registered_systems() -> List[RegisteredSystem]:
    return list(SYSTEM_REGISTRY.values())


def list_actively_evaluated_systems() -> List[RegisteredSystem]:
    return [
        s for s in SYSTEM_REGISTRY.values()
        if s.evaluation_status == SystemEvaluationStatus.REGISTERED_AND_EVALUATED
    ]
