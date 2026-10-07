"""B5 HistGradientBoosting Complexity Classifier."""

from typing import Optional
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from app.complexity_analysis.models.base import BaseComplexityClassifier


class HistGradientBoostingComplexityClassifier(BaseComplexityClassifier):
    """Histogram-based Gradient Boosting classifier (scikit-learn)."""

    def __init__(
        self,
        max_iter: int = 100,
        max_leaf_nodes: int = 31,
        min_samples_leaf: int = 10,
        random_state: int = 42,
    ):
        super().__init__(model_id="B5", model_name="Hist_Gradient_Boosting_Classifier")
        self.clf = HistGradientBoostingClassifier(
            max_iter=max_iter,
            max_leaf_nodes=max_leaf_nodes,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "HistGradientBoostingComplexityClassifier":
        self.clf.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")
        return self.clf.predict_proba(X)
