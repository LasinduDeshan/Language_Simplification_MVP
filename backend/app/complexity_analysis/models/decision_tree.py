"""B3 Constrained Decision Tree Classifier."""

from typing import Optional
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from app.complexity_analysis.models.base import BaseComplexityClassifier


class ConstrainedDecisionTreeClassifier(BaseComplexityClassifier):
    """Shallow, interpretable decision tree with bounded depth."""

    def __init__(self, max_depth: int = 4, min_samples_leaf: int = 10, random_state: int = 42):
        super().__init__(model_id="B3", model_name="Constrained_Decision_Tree")
        self.clf = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ConstrainedDecisionTreeClassifier":
        self.clf.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Model not fitted.")
        return self.clf.predict_proba(X)

    def get_feature_importances(self) -> Optional[np.ndarray]:
        if not self.is_fitted:
            return None
        return self.clf.feature_importances_
