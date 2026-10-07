"""B4 Random Forest Complexity Classifier."""

from typing import Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.complexity_analysis.models.base import BaseComplexityClassifier


class RandomForestComplexityClassifier(BaseComplexityClassifier):
    """Ensemble of shallow decision trees with feature importance tracking."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        min_samples_leaf: int = 5,
        random_state: int = 42,
    ):
        super().__init__(model_id="B4", model_name="Random_Forest_Classifier")
        self.clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            oob_score=True,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "RandomForestComplexityClassifier":
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
