"""End-to-end integration tests for Stage 22 Complexity Analysis pipeline."""

from app.complexity_analysis.repositories.model_repository import ModelRepository
from app.complexity_analysis.repositories.feature_repository import FeatureRepository
from app.complexity_analysis.pipeline import ComplexityAnalysisPipeline
from app.complexity_analysis.schemas import ComplexityClassificationResult


def test_stage22_pipeline_end_to_end():
    model_repo = ModelRepository()
    pkg = model_repo.load_package()

    pipeline = ComplexityAnalysisPipeline(
        classifier=pkg["classifier"],
        feature_builder=pkg["feature_builder"],
        calibrator=pkg["calibrator"],
        ood_detector=pkg["ood_detector"],
    )

    feat_repo = FeatureRepository()
    df_feats = feat_repo.load_features_df()
    sample_records = df_feats.head(10).to_dict(orient="records")

    results = pipeline.classify_batch(sample_records)
    assert len(results) == 10

    for res in results:
        assert isinstance(res, ComplexityClassificationResult)
        assert res.predicted_difficulty in ("easy", "medium", "hard")
        assert 0.0 <= res.confidence <= 1.0
        assert sum(res.class_probabilities.values()) == pytest.approx(1.0, abs=1e-3)
        assert len(res.complexity_factors) >= 1
        assert res.record_hash
        assert res.model_version == "1.0.0"


import pytest
