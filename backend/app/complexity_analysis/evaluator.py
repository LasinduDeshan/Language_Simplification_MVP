"""Multi-class evaluation, safety-critical error analysis, and Wilson CI module."""

from typing import Dict, List, Tuple
import math
import numpy as np
import pandas as pd
from sklearn.metrics import (
    f1_score,
    balanced_accuracy_score,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)
from app.complexity_analysis.schemas import ModelEvaluationSummary
from app.complexity_analysis.calibration import compute_expected_calibration_error


def compute_wilson_score_interval(
    successes: int,
    total: int,
    confidence: float = 0.95,
) -> Tuple[float, float]:
    """Computes the Wilson score binomial confidence interval."""
    if total == 0:
        return 0.0, 0.0

    z = 1.95996  # for 95% confidence
    p_hat = successes / total
    denominator = 1.0 + (z**2) / total
    center = p_hat + (z**2) / (2.0 * total)
    spread = z * math.sqrt((p_hat * (1.0 - p_hat) / total) + ((z**2) / (4.0 * total**2)))

    lower = max(0.0, (center - spread) / denominator)
    upper = min(1.0, (center + spread) / denominator)
    return float(lower), float(upper)


class ModelEvaluator:
    """Evaluates candidate models against multi-class metrics and safety error constraints."""

    CLASSES: List[str] = ["easy", "medium", "hard"]

    @classmethod
    def evaluate(
        cls,
        model_id: str,
        model_name: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        split_name: str = "validation",
        fit_time_seconds: float = 0.0,
        latency_ms: float = 0.0,
    ) -> Tuple[ModelEvaluationSummary, pd.DataFrame]:
        """Calculates full evaluation summary and confusion matrix DataFrame."""
        sample_count = len(y_true)
        macro_f1 = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        weighted_f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
        balanced_acc = float(balanced_accuracy_score(y_true, y_pred))
        acc = float(accuracy_score(y_true, y_pred))

        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=[0, 1, 2], zero_division=0
        )

        per_class_rec = {cls.CLASSES[i]: float(rec[i]) for i in range(3)}
        per_class_prec = {cls.CLASSES[i]: float(prec[i]) for i in range(3)}
        per_class_f1 = {cls.CLASSES[i]: float(f1[i]) for i in range(3)}

        ece = compute_expected_calibration_error(y_true, y_prob)

        # Safety-critical Hard-to-Easy error: Actual Hard (index 2) predicted as Easy (index 0)
        hard_mask = (y_true == 2)
        total_hard = int(np.sum(hard_mask))
        hard_to_easy_count = int(np.sum((y_true == 2) & (y_pred == 0)))
        hard_to_easy_rate = (hard_to_easy_count / total_hard) if total_hard > 0 else 0.0

        ci_low, ci_high = compute_wilson_score_interval(hard_to_easy_count, total_hard)

        summary = ModelEvaluationSummary(
            model_id=model_id,
            model_name=model_name,
            split_evaluated=split_name,
            sample_count=sample_count,
            macro_f1=macro_f1,
            weighted_f1=weighted_f1,
            balanced_accuracy=balanced_acc,
            accuracy=acc,
            per_class_recall=per_class_rec,
            per_class_precision=per_class_prec,
            per_class_f1=per_class_f1,
            expected_calibration_error=ece,
            hard_to_easy_error_rate=hard_to_easy_rate,
            hard_to_easy_error_count=hard_to_easy_count,
            hard_to_easy_wilson_ci_lower=ci_low,
            hard_to_easy_wilson_ci_upper=ci_high,
            fit_time_seconds=fit_time_seconds,
            inference_latency_ms_per_item=latency_ms,
        )

        cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
        cm_df = pd.DataFrame(
            cm,
            index=[f"Actual_{c}" for c in cls.CLASSES],
            columns=[f"Pred_{c}" for c in cls.CLASSES],
        )

        return summary, cm_df
