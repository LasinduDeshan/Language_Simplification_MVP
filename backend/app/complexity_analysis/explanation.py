"""Explainability and ComplexityFactor generation module for Stage 22."""

from typing import Any, Dict, List, Optional
from app.complexity_analysis.schemas import ComplexityFactor, DifficultyLabel


EXPLANATION_RULES = [
    {
        "feature": "avg_sentence_length",
        "threshold_high": 12.0,
        "code_high": "LONG_AVERAGE_SENTENCE",
        "dir_high": "increases",
        "threshold_low": 6.0,
        "code_low": "SHORT_SIMPLE_STRUCTURE",
        "dir_low": "reduces",
    },
    {
        "feature": "max_dependency_depth",
        "threshold_high": 4.0,
        "code_high": "HIGH_DEPENDENCY_DEPTH",
        "dir_high": "increases",
        "threshold_low": 2.0,
        "code_low": "SHALLOW_PARSE_TREE",
        "dir_low": "reduces",
    },
    {
        "feature": "clause_count",
        "threshold_high": 2.0,
        "code_high": "MULTIPLE_SUBORDINATE_CLAUSES",
        "dir_high": "increases",
        "threshold_low": 0.0,
        "code_low": "SINGLE_MAIN_CLAUSE",
        "dir_low": "reduces",
    },
    {
        "feature": "long_word_ratio",
        "threshold_high": 0.20,
        "code_high": "ADVANCED_LEXICAL_DENSITY",
        "dir_high": "increases",
        "threshold_low": 0.05,
        "code_low": "BASIC_VOCABULARY_DOMINANT",
        "dir_low": "reduces",
    },
    {
        "feature": "negation_count",
        "threshold_high": 1.0,
        "code_high": "NEGATION_LOAD",
        "dir_high": "increases",
        "threshold_low": 0.0,
        "code_low": "NO_NEGATION_STRUCTURES",
        "dir_low": "reduces",
    },
    {
        "feature": "passive_voice",
        "threshold_high": 1.0,
        "code_high": "PASSIVE_VOICE_STRUCTURE",
        "dir_high": "increases",
        "threshold_low": 0.0,
        "code_low": "ACTIVE_VOICE_STRUCTURE",
        "dir_low": "reduces",
    },
]


class ComplexityExplainer:
    """Generates structured ComplexityFactor objects with evidence codes."""

    def generate_factors(
        self,
        features: Dict[str, Any],
        predicted_difficulty: DifficultyLabel,
        feature_importances: Optional[Dict[str, float]] = None,
    ) -> List[ComplexityFactor]:
        """Evaluates features against explainability rules and returns top factors."""
        factors: List[ComplexityFactor] = []
        importances = feature_importances or {}

        for rule in EXPLANATION_RULES:
            feat_name = rule["feature"]
            if feat_name not in features:
                continue

            val = float(features[feat_name])
            imp = importances.get(feat_name)

            if val >= rule["threshold_high"]:
                factors.append(
                    ComplexityFactor(
                        feature_name=feat_name,
                        observed_value=val,
                        contribution_direction=rule["dir_high"],  # type: ignore
                        importance=imp,
                        explanation_code=rule["code_high"],
                    )
                )
            elif val <= rule["threshold_low"]:
                factors.append(
                    ComplexityFactor(
                        feature_name=feat_name,
                        observed_value=val,
                        contribution_direction=rule["dir_low"],  # type: ignore
                        importance=imp,
                        explanation_code=rule["code_low"],
                    )
                )

        # Default fallback if no specific rule triggered
        if not factors:
            factors.append(
                ComplexityFactor(
                    feature_name="word_count",
                    observed_value=float(features.get("word_count", 0)),
                    contribution_direction="neutral",
                    importance=importances.get("word_count"),
                    explanation_code="MODERATE_LEXICAL_LENGTH",
                )
            )

        return factors
