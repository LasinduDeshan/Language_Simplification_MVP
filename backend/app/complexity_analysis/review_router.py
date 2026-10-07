"""Threshold-based confidence and review routing for Stage 22."""

from typing import Dict, List, Tuple
import numpy as np
from app.complexity_analysis.schemas import DifficultyLabel


class ReviewRouter:
    """Routes classifications to automatic acceptance or human review queue."""

    def __init__(
        self,
        confidence_threshold: float = 0.80,
        margin_threshold: float = 0.15,
    ):
        self.confidence_threshold = confidence_threshold
        self.margin_threshold = margin_threshold

    def evaluate_routing(
        self,
        class_probabilities: Dict[DifficultyLabel, float],
        is_out_of_distribution: bool = False,
        ood_violations: List[str] = None,
        parser_failed: bool = False,
    ) -> Tuple[bool, List[str], float, float]:
        """Evaluates whether an instance requires manual review.

        Returns:
            (review_required, review_reasons, confidence, margin)
        """
        ood_violations = ood_violations or []
        review_reasons: List[str] = []

        probs = list(class_probabilities.values())
        sorted_probs = sorted(probs, reverse=True)

        confidence = float(sorted_probs[0]) if len(sorted_probs) > 0 else 0.0
        second_prob = float(sorted_probs[1]) if len(sorted_probs) > 1 else 0.0
        margin = float(confidence - second_prob)

        # 1. Parser failure
        if parser_failed:
            review_reasons.append("NLP preprocessing parser failed on input text")

        # 2. Out-of-distribution
        if is_out_of_distribution:
            violations_str = ", ".join(ood_violations[:3])
            review_reasons.append(f"Input features out-of-distribution ({violations_str})")

        # 3. Confidence threshold
        if confidence < self.confidence_threshold:
            review_reasons.append(
                f"Prediction confidence ({confidence:.3f}) below threshold ({self.confidence_threshold:.2f})"
            )

        # 4. Margin threshold
        if margin < self.margin_threshold:
            review_reasons.append(
                f"Probability margin ({margin:.3f}) below threshold ({self.margin_threshold:.2f})"
            )

        review_required = len(review_reasons) > 0
        return review_required, review_reasons, confidence, margin
