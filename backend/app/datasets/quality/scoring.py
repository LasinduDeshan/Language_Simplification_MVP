"""Transparent multi-dimensional quality scoring and mutually exclusive precedence engine."""
from typing import List, Dict, Tuple
from app.datasets.quality.enums import QualityStatus, RuleSeverity, QualityDimension
from app.datasets.quality.schemas import QualityRuleResultV1, QualityScoreBreakdownV1
from app.datasets.quality.thresholds import (
    SCORE_PASS_MINIMUM,
    SCORE_REVIEW_MINIMUM,
    CORPUS_DIMENSION_WEIGHTS
)


class QualityScorer:
    """Computes transparent scores and resolves final record quality disposition."""

    @classmethod
    def calculate_scores(cls, results: List[QualityRuleResultV1]) -> Tuple[QualityScoreBreakdownV1, float]:
        """Calculates dimension scores and overall weighted score without masking failures."""
        dimension_penalties: Dict[str, float] = {
            "meaning_preservation": 0.0,
            "grammar_fluency": 0.0,
            "simplicity_improvement": 0.0,
            "age_appropriateness": 0.0,
            "safety_answer_boundary": 0.0,
        }

        for res in results:
            dim_key = res.dimension.value if res.dimension else "metadata_integrity"
            if dim_key in dimension_penalties and not res.passed:
                if res.severity == RuleSeverity.CRITICAL:
                    dimension_penalties[dim_key] += 100.0  # Immediate dimension zeroing
                elif res.severity == RuleSeverity.ERROR:
                    dimension_penalties[dim_key] += 40.0
                elif res.severity == RuleSeverity.WARNING:
                    dimension_penalties[dim_key] += 15.0
                elif res.severity == RuleSeverity.INFO:
                    dimension_penalties[dim_key] += 2.0

        scores = {}
        for dim, penalty in dimension_penalties.items():
            scores[dim] = max(0.0, min(100.0, 100.0 - penalty))

        # Calculate overall weighted score
        overall = sum(scores[dim] * CORPUS_DIMENSION_WEIGHTS[dim] for dim in CORPUS_DIMENSION_WEIGHTS)
        overall = max(0.0, min(100.0, overall))

        breakdown = QualityScoreBreakdownV1(
            meaning_preservation=scores["meaning_preservation"],
            grammar_fluency=scores["grammar_fluency"],
            simplicity_improvement=scores["simplicity_improvement"],
            age_appropriateness=scores["age_appropriateness"],
            safety_answer_boundary=scores["safety_answer_boundary"],
            overall_score=overall
        )
        return breakdown, overall

    @classmethod
    def resolve_status(
        cls,
        results: List[QualityRuleResultV1],
        overall_score: float
    ) -> Tuple[QualityStatus, int, int, int]:
        """
        Resolves final record disposition using strict mutually exclusive precedence:
        quarantined -> automatic_check_failed -> manual_review_required -> automatic_check_passed
        """
        critical_count = sum(1 for r in results if r.severity == RuleSeverity.CRITICAL and not r.passed)
        error_count = sum(1 for r in results if r.severity == RuleSeverity.ERROR and not r.passed)
        warning_count = sum(1 for r in results if r.severity == RuleSeverity.WARNING and not r.passed)

        # 1. Any CRITICAL failure -> QUARANTINED
        if critical_count > 0:
            return QualityStatus.QUARANTINED, warning_count, error_count, critical_count

        # 2. Any ERROR failure OR score < 70.0 -> AUTOMATIC_CHECK_FAILED
        if error_count > 0 or overall_score < SCORE_REVIEW_MINIMUM:
            return QualityStatus.AUTOMATIC_CHECK_FAILED, warning_count, error_count, critical_count

        # 3. Any WARNING failure OR 70.0 <= score < 85.0 -> MANUAL_REVIEW_REQUIRED
        if warning_count > 0 or overall_score < SCORE_PASS_MINIMUM:
            return QualityStatus.MANUAL_REVIEW_REQUIRED, warning_count, error_count, critical_count

        # 4. All checks passed and score >= 85.0 -> AUTOMATIC_CHECK_PASSED
        return QualityStatus.AUTOMATIC_CHECK_PASSED, warning_count, error_count, critical_count
