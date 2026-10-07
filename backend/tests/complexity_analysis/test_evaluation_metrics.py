"""Unit tests for ModelEvaluator and Wilson score confidence intervals."""

import numpy as np
from app.complexity_analysis.evaluator import (
    ModelEvaluator,
    compute_wilson_score_interval,
)


def test_wilson_score_interval():
    low, high = compute_wilson_score_interval(successes=0, total=100)
    assert low == 0.0
    assert high < 0.05

    low_mid, high_mid = compute_wilson_score_interval(successes=50, total=100)
    assert 0.40 <= low_mid <= 0.50
    assert 0.50 <= high_mid <= 0.60


def test_model_evaluator_hard_to_easy_rate():
    # 0 = easy, 1 = med, 2 = hard
    y_true = np.array([2, 2, 2, 2, 0, 1])
    y_pred = np.array([0, 2, 2, 1, 0, 1])  # 1 out of 4 hard predicted as easy -> 25%
    y_prob = np.array([
        [0.8, 0.1, 0.1],
        [0.1, 0.1, 0.8],
        [0.1, 0.1, 0.8],
        [0.1, 0.8, 0.1],
        [0.9, 0.05, 0.05],
        [0.1, 0.8, 0.1],
    ])

    summary, cm_df = ModelEvaluator.evaluate(
        model_id="TEST",
        model_name="TestModel",
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
    )

    assert summary.hard_to_easy_error_count == 1
    assert summary.hard_to_easy_error_rate == 0.25
    assert summary.hard_to_easy_wilson_ci_lower < 0.25 < summary.hard_to_easy_wilson_ci_upper
    assert cm_df.shape == (3, 3)
