"""
Baseline Simplification package for Stage 24 English baseline methods, evaluation, and registry.
"""
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    BaselineConfiguration,
    BaselineOutputRecord,
    FinalDisposition,
    MeaningValidationStatus,
    ProtectedElementSource,
    AgeConfiguration,
)
from app.baseline_simplification.registry import BaselineRegistry, DEFAULT_CONFIGURATIONS
from app.baseline_simplification.protected_meaning_validator import ProtectedMeaningValidator
from app.baseline_simplification.output_validator import OutputValidator
from app.baseline_simplification.identity_baseline import IdentityBaseline
from app.baseline_simplification.lexical_baseline import LexicalSubstitutionBaseline
from app.baseline_simplification.sentence_split_baseline import SentenceSplitBaseline
from app.baseline_simplification.syntactic_rule_baseline import SyntacticRuleBaseline
from app.baseline_simplification.combined_baseline import CombinedDeterministicBaseline
from app.baseline_simplification.offline_fallback_adapter import OfflineFallbackAdapter
from app.baseline_simplification.runner import BaselineRunner
from app.baseline_simplification.evaluator import BaselineEvaluator

__all__ = [
    "BaselineMethodId",
    "BaselineConfiguration",
    "BaselineOutputRecord",
    "FinalDisposition",
    "MeaningValidationStatus",
    "ProtectedElementSource",
    "AgeConfiguration",
    "BaselineRegistry",
    "DEFAULT_CONFIGURATIONS",
    "ProtectedMeaningValidator",
    "OutputValidator",
    "IdentityBaseline",
    "LexicalSubstitutionBaseline",
    "SentenceSplitBaseline",
    "SyntacticRuleBaseline",
    "CombinedDeterministicBaseline",
    "OfflineFallbackAdapter",
    "BaselineRunner",
    "BaselineEvaluator",
]
