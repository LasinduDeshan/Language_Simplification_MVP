"""B0 Majority-Class Baseline Classifier."""

import numpy as np
from app.complexity_analysis.models.base import BaseComplexityClassifier


class MajorityBaselineClassifier(BaseComplexityClassifier):
    """Predicts the modal class observed in the training distribution."""

    def __init__(self):
        super().__init__(model_id="B0", model_name="Majority_Class_Baseline")
        self.majority_class_idx: int = 0
        self.class_priors: np.ndarray = np.array([0.333, 0.333, 0.334])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MajorityBaselineClassifier":
        counts = np.bincount(y, minlength=3)
        self.majority_class_idx = int(np.argmax(counts))
        self.class_priors = counts.astype(float) / float(len(y))
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")
        n_samples = len(X)
        return np.tile(self.class_priors, (n_samples, 1))
