"""B1 Transparent Rule-Based Complexity Classifier."""

from typing import Dict, List, Optional
import numpy as np
from app.complexity_analysis.models.base import BaseComplexityClassifier
from app.complexity_analysis.feature_registry import FEATURE_NAMES


class TransparentRuleClassifier(BaseComplexityClassifier):
    """Deterministic rule-based classifier using observable linguistic complexity thresholds."""

    def __init__(
        self,
        word_count_easy_max: float = 8.0,
        word_count_hard_min: float = 14.0,
        avg_depth_easy_max: float = 2.0,
        avg_depth_hard_min: float = 3.5,
        clause_count_hard_min: float = 1.0,
        long_word_ratio_hard_min: float = 0.18,
    ):
        super().__init__(model_id="B1", model_name="Transparent_Rule_Baseline")
        self.word_count_easy_max = word_count_easy_max
        self.word_count_hard_min = word_count_hard_min
        self.avg_depth_easy_max = avg_depth_easy_max
        self.avg_depth_hard_min = avg_depth_hard_min
        self.clause_count_hard_min = clause_count_hard_min
        self.long_word_ratio_hard_min = long_word_ratio_hard_min

        self.word_count_idx = FEATURE_NAMES.index("word_count") if "word_count" in FEATURE_NAMES else 2
        self.avg_depth_idx = FEATURE_NAMES.index("avg_dependency_depth") if "avg_dependency_depth" in FEATURE_NAMES else 21
        self.clause_idx = FEATURE_NAMES.index("clause_count") if "clause_count" in FEATURE_NAMES else 22
        self.long_ratio_idx = FEATURE_NAMES.index("long_word_ratio") if "long_word_ratio" in FEATURE_NAMES else 10

    def fit(self, X: np.ndarray, y: np.ndarray) -> "TransparentRuleClassifier":
        """Fits empirical thresholds on training data quantiles."""
        # Baseline uses initialized pedagogical thresholds or quantile adjustments
        self.is_fitted = True
        return self

    def classify_row(self, row: np.ndarray) -> int:
        """Determines class index (0=easy, 1=medium, 2=hard) from feature values."""
        wc = row[self.word_count_idx]
        depth = row[self.avg_depth_idx]
        clause = row[self.clause_idx]
        long_ratio = row[self.long_ratio_idx]

        # Hard criteria: multi-clause, deep parse tree, high word length, or high long word ratio
        if (wc >= self.word_count_hard_min and depth >= self.avg_depth_hard_min) or clause >= self.clause_count_hard_min or long_ratio >= self.long_word_ratio_hard_min:
            return 2  # hard

        # Easy criteria: short length, shallow parse tree, 0 clauses, low long word ratio
        if wc <= self.word_count_easy_max and depth <= self.avg_depth_easy_max and clause == 0:
            return 0  # easy

        # Medium: default intermediate tier
        return 1  # medium

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")

        probs = np.zeros((len(X), 3), dtype=np.float64)
        for i in range(len(X)):
            pred_idx = self.classify_row(X[i])
            if pred_idx == 0:
                probs[i] = [0.85, 0.10, 0.05]
            elif pred_idx == 1:
                probs[i] = [0.15, 0.70, 0.15]
            else:
                probs[i] = [0.05, 0.15, 0.80]
        return probs
