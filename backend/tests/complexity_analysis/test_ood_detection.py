"""Unit tests for deterministic Q0.01-Q0.99 OODDetector."""

import pandas as pd
from app.complexity_analysis.ood_detector import OODDetector
from app.complexity_analysis.feature_builder import FeatureBuilder


def test_ood_detector_learns_bounds():
    records = []
    for val in range(100):
        records.append({
            "char_count": val * 5,
            "word_count": val,
            "sentence_count": 1,
            "token_count": val,
            "passive_voice": False,
        })
    builder = FeatureBuilder()
    df_train = builder.build_feature_dataframe(records)

    detector = OODDetector(lower_quantile=0.01, upper_quantile=0.99)
    detector.fit(df_train, text_roles=["source_text", "simplified_text"])

    assert detector.is_fitted
    assert "word_count" in detector.feature_bounds
    assert detector.feature_bounds["word_count"][0] >= 0.0


def test_in_distribution_instance():
    builder = FeatureBuilder()
    records = [{"word_count": i, "char_count": i * 5} for i in range(100)]
    df_train = builder.build_feature_dataframe(records)

    detector = OODDetector(lower_quantile=0.01, upper_quantile=0.99)
    detector.fit(df_train, text_roles=["source_text"])

    test_features = {"word_count": 50.0, "char_count": 250.0, "passive_voice": 0.0}
    res = detector.evaluate_instance(features=test_features, text_role="source_text")
    assert not res.is_out_of_distribution
    assert res.anomaly_score == 0.0


def test_out_of_distribution_continuous_and_unseen_role():
    builder = FeatureBuilder()
    records = [{"word_count": i, "char_count": i * 5} for i in range(100)]
    df_train = builder.build_feature_dataframe(records)

    detector = OODDetector(lower_quantile=0.01, upper_quantile=0.99)
    detector.fit(df_train, text_roles=["source_text"])

    # Massive outlier word count
    outlier_features = {"word_count": 9999.0, "char_count": 50000.0, "passive_voice": 0.0}
    res = detector.evaluate_instance(features=outlier_features, text_role="unknown_third_party_role")
    assert res.is_out_of_distribution
    assert any("unseen_text_role" in v for v in res.violating_features)


def test_parser_failure_triggers_immediate_ood():
    detector = OODDetector()
    detector.is_fitted = True
    res = detector.evaluate_instance(features={}, parser_failed=True)
    assert res.is_out_of_distribution
    assert "parser_failure" in res.violating_features
