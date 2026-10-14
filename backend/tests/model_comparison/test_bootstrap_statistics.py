"""
Test statistical tests: Wilcoxon signed-rank, rank-biserial effect sizes, and bootstrap SacreBLEU difference.
"""
import pytest
from app.model_comparison.statistics import (
    paired_wilcoxon_test,
    paired_sensitivity_ttest,
    paired_bootstrap_sacrebleu_difference,
    benjamini_hochberg_fdr,
)


def test_wilcoxon_paired_and_effect_size():
    # Model A consistently better than Model B
    scores_a = [55.0, 60.0, 58.0, 62.0, 65.0, 59.0, 63.0, 67.0, 64.0, 61.0]
    scores_b = [45.0, 48.0, 50.0, 51.0, 53.0, 49.0, 52.0, 55.0, 54.0, 50.0]

    res = paired_wilcoxon_test(scores_a, scores_b)
    assert res["n_total"] == 10
    assert res["n_zero_diff"] == 0
    assert res["p_value"] < 0.05
    assert res["rank_biserial_r"] > 0.8  # Strong positive effect


def test_wilcoxon_identical_scores():
    scores = [50.0, 50.0, 50.0, 50.0]
    res = paired_wilcoxon_test(scores, scores)
    assert res["n_zero_diff"] == 4
    assert res["p_value"] == 1.0
    assert res["rank_biserial_r"] == 0.0
    assert res["test_status"] == "NOT_APPLICABLE_ALL_DIFFERENCES_ZERO"
    assert res["p_method"] == "none"
    assert res["continuity_correction"] is False


def test_wilcoxon_explicit_scipy_approx_arguments(monkeypatch):
    """
    Stage 28A explicitly uses SciPy's continuity-corrected asymptotic normal approximation
    with zero_method="wilcox", correction=True, alternative="two-sided" and method="approx".
    """
    import scipy.stats as stats

    captured_kwargs = {}
    orig_wilcoxon = stats.wilcoxon

    def mock_wilcoxon(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return orig_wilcoxon(*args, **kwargs)

    monkeypatch.setattr(stats, "wilcoxon", mock_wilcoxon)

    scores_a = [55.0, 60.0, 58.0, 62.0]
    scores_b = [45.0, 48.0, 50.0, 51.0]
    res = paired_wilcoxon_test(scores_a, scores_b)

    assert captured_kwargs["zero_method"] == "wilcox"
    assert captured_kwargs["correction"] is True
    assert captured_kwargs["alternative"] == "two-sided"
    assert captured_kwargs["method"] == "approx"
    assert res["p_method"] == "asymptotic_normal"
    assert res["continuity_correction"] is True
    assert res["test_status"] == "COMPUTED"


def test_parametric_sensitivity_ttest():
    scores_a = [55.0, 60.0, 58.0, 62.0, 65.0]
    scores_b = [45.0, 48.0, 50.0, 51.0, 53.0]
    res = paired_sensitivity_ttest(scores_a, scores_b)
    assert res["mean_diff"] > 0
    assert res["p_value"] < 0.05
    assert res["cohens_dz"] > 1.0


def test_bootstrap_corpus_bleu_difference():
    preds_a = ["The cat sat on the mat.", "The dog barked loudly."]
    preds_b = ["A cat sat.", "A dog barked."]
    refs = [["The cat sat on the mat."], ["The dog barked loudly."]]

    res = paired_bootstrap_sacrebleu_difference(preds_a, preds_b, refs, n_iterations=100, seed=42)
    assert res["requested_iterations"] == 100
    assert "observed_difference" in res
    assert res["observed_difference"] >= 0  # Preds A matches refs perfectly


def test_benjamini_hochberg_fdr():
    p_vals = [0.001, 0.01, 0.04, 0.07, 0.15]
    adj = benjamini_hochberg_fdr(p_vals, alpha=0.05)
    assert len(adj) == 5
    # Adjusted p-values should be monotonically increasing
    for i in range(len(adj) - 1):
        assert adj[i]["adjusted_p_value"] <= adj[i + 1]["adjusted_p_value"]
    assert adj[0]["significant_at_alpha"] is True
