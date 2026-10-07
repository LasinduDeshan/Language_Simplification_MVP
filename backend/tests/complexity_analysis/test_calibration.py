"""Unit tests for probability calibration and ECE calculation."""

import numpy as np
from app.complexity_analysis.calibration import (
    ProbabilityCalibrator,
    compute_expected_calibration_error,
)


def test_ece_computation():
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_prob = np.array([
        [0.9, 0.05, 0.05],
        [0.1, 0.8, 0.1],
        [0.05, 0.05, 0.9],
        [0.7, 0.2, 0.1],
        [0.2, 0.7, 0.1],
        [0.1, 0.1, 0.8],
    ])
    ece = compute_expected_calibration_error(y_true, y_prob)
    assert 0.0 <= ece <= 1.0


def test_probability_calibrator_isotonic():
    oof_probs = np.array([
        [0.8, 0.1, 0.1],
        [0.7, 0.2, 0.1],
        [0.1, 0.8, 0.1],
        [0.2, 0.7, 0.1],
        [0.05, 0.15, 0.8],
        [0.1, 0.1, 0.8],
    ])
    y_true = np.array([0, 0, 1, 1, 2, 2])

    cal = ProbabilityCalibrator(method="isotonic")
    cal.fit(oof_probs, y_true)
    assert cal.is_fitted

    uncal = np.array([[0.75, 0.15, 0.10], [0.10, 0.10, 0.80]])
    calibrated = cal.calibrate(uncal)
    assert calibrated.shape == (2, 3)
    np.testing.assert_allclose(calibrated.sum(axis=1), np.ones(2), atol=1e-5)
