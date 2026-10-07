"""Unit tests for all Stage 22 baseline and ML model candidates (B0-B5)."""

import numpy as np
from app.complexity_analysis.models import (
    MajorityBaselineClassifier,
    TransparentRuleClassifier,
    MultinomialLogisticClassifier,
    ConstrainedDecisionTreeClassifier,
    RandomForestComplexityClassifier,
    HistGradientBoostingComplexityClassifier,
)


def get_synthetic_data():
    X = np.array([
        [10.0, 2.0, 1.0, 1.0, 0.0, 4.0, 2.0, 3, 1.5, 0, 0.0, 0.9, 1, 0.5, 1, 0.5, 0, 0.0, 0, 0.0, 0.8, 0.2, 2.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [30.0, 6.0, 5.0, 1.0, 1.0, 5.0, 6.0, 9, 1.8, 1, 0.2, 0.8, 2, 0.4, 2, 0.4, 1, 0.2, 0, 0.0, 0.7, 0.3, 4.0, 2.0, 1.0, 0.0, 1.0, 0.0],
        [80.0, 16.0, 14.0, 2.0, 2.0, 6.0, 8.0, 25, 1.8, 4, 0.3, 0.7, 5, 0.35, 4, 0.28, 3, 0.2, 1, 0.07, 0.6, 0.4, 7.0, 3.5, 2.0, 1.0, 1.0, 1.0],
    ])
    y = np.array([0, 1, 2])
    return X, y


def test_b0_majority():
    X, y = get_synthetic_data()
    m = MajorityBaselineClassifier()
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)


def test_b1_rule_based():
    X, y = get_synthetic_data()
    m = TransparentRuleClassifier()
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)
    preds = m.predict(X)
    assert len(preds) == 3


def test_b2_logistic():
    X, y = get_synthetic_data()
    m = MultinomialLogisticClassifier()
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)


def test_b3_tree():
    X, y = get_synthetic_data()
    m = ConstrainedDecisionTreeClassifier(max_depth=2, min_samples_leaf=1)
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)


def test_b4_random_forest():
    X, y = get_synthetic_data()
    m = RandomForestComplexityClassifier(n_estimators=10, max_depth=3, min_samples_leaf=1)
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)


def test_b5_hist_gradient_boosting():
    X, y = get_synthetic_data()
    m = HistGradientBoostingComplexityClassifier(max_iter=10, min_samples_leaf=1)
    m.fit(X, y)
    probs = m.predict_proba(X)
    assert probs.shape == (3, 3)
