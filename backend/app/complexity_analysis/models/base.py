"""Abstract base classifier class for Stage 22 complexity models."""

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np


class BaseComplexityClassifier(ABC):
    """Abstract interface for all difficulty classification candidates."""

    CLASSES: List[str] = ["easy", "medium", "hard"]

    def __init__(self, model_id: str, model_name: str):
        self.model_id = model_id
        self.model_name = model_name
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseComplexityClassifier":
        """Fits the classifier on training features and integer targets (0=easy, 1=med, 2=hard)."""
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predicts class probabilities array of shape (N, 3)."""
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predicts integer class labels (0=easy, 1=medium, 2=hard)."""
        probs = self.predict_proba(X)
        return np.argmax(probs, axis=1)

    def get_feature_importances(self) -> Optional[np.ndarray]:
        """Optional feature importance vector."""
        return None
