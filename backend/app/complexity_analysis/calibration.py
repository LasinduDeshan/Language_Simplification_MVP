"""Probability calibration and Expected Calibration Error (ECE) module for Stage 22."""

from typing import Any, Dict, List, Literal, Optional, Tuple
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def compute_expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Computes Expected Calibration Error (ECE) for multi-class predictions."""
    preds = np.argmax(y_prob, axis=1)
    confs = np.max(y_prob, axis=1)
    accuracies = (preds == y_true)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confs > bin_lower) & (confs <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confs[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return float(ece)


class ProbabilityCalibrator:
    """Multi-class probability calibrator fitted strictly on Out-Of-Fold (OOF) training predictions."""

    def __init__(self, method: Literal["isotonic", "sigmoid"] = "isotonic"):
        self.method = method
        self.calibrators: Dict[int, Any] = {}
        self.classes: List[str] = ["easy", "medium", "hard"]
        self.is_fitted = False

    def fit(self, oof_probs: np.ndarray, y_true: np.ndarray) -> "ProbabilityCalibrator":
        """Fits calibration models per class on out-of-fold predicted probabilities."""
        n_classes = oof_probs.shape[1]
        self.calibrators.clear()

        for c in range(n_classes):
            y_binary = (y_true == c).astype(float)
            p_c = np.clip(oof_probs[:, c], 1e-6, 1.0 - 1e-6)

            if self.method == "isotonic":
                cal = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
                cal.fit(p_c, y_binary)
            else:
                # Sigmoid / Platt scaling
                cal = LogisticRegression(C=1.0, solver="lbfgs")
                log_odds = np.log(p_c / (1.0 - p_c)).reshape(-1, 1)
                cal.fit(log_odds, y_binary)

            self.calibrators[c] = cal

        self.is_fitted = True
        return self

    def calibrate(self, uncalibrated_probs: np.ndarray) -> np.ndarray:
        """Calibrates predicted probabilities and normalizes across classes to sum to 1.0."""
        if not self.is_fitted:
            return uncalibrated_probs

        n_samples, n_classes = uncalibrated_probs.shape
        calibrated = np.zeros_like(uncalibrated_probs)

        for c in range(n_classes):
            p_c = np.clip(uncalibrated_probs[:, c], 1e-6, 1.0 - 1e-6)
            if self.method == "isotonic":
                calibrated[:, c] = self.calibrators[c].predict(p_c)
            else:
                log_odds = np.log(p_c / (1.0 - p_c)).reshape(-1, 1)
                calibrated[:, c] = self.calibrators[c].predict_proba(log_odds)[:, 1]

        # Re-normalize to ensure rows sum to 1.0
        row_sums = calibrated.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return calibrated / row_sums
