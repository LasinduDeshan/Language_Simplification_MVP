"""B2 Multinomial Logistic Regression Classifier."""

from typing import Optional
import numpy as np
from sklearn.linear_model import LogisticRegression
from app.complexity_analysis.models.base import BaseComplexityClassifier


class MultinomialLogisticClassifier(BaseComplexityClassifier):
    """L2-regularized multinomial logistic regression on standardized complexity features."""

    def __init__(self, C: float = 1.0, random_state: int = 42):
        super().__init__(model_id="B2", model_name="Multinomial_Logistic_Regression")
        self.clf = LogisticRegression(
            multi_class="multinomial",
            solver="lbfgs",
            C=C,
            max_iter=1000,
            random_state=random_state,
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "MultinomialLogisticClassifier":
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
        # Mean absolute coefficients across the 3 classes
        return np.mean(np.abs(self.clf.coef_), axis=0)
