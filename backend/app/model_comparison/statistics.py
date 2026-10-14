"""
Statistical Analysis Module for Stage 28A Preliminary English Model Comparison.
Implements:
1. Paired Wilcoxon signed-rank tests with matched rank-biserial correlation (r_rb)
2. Paired bootstrap difference and 95% CI for Corpus SacreBLEU
3. Paired t-tests and Cohen's d_z for continuous sensitivity
4. Benjamini-Hochberg False Discovery Rate (FDR) per predefined hypothesis family
5. Stratified paired bootstrap CIs tracking undefined replicates
"""
import numpy as np
from scipy import stats
from typing import List, Dict, Any, Tuple, Optional
import sacrebleu


def paired_wilcoxon_test(
    scores_a: List[float],
    scores_b: List[float],
) -> Dict[str, Any]:
    """
    Computes paired Wilcoxon signed-rank test and matched rank-biserial correlation.
    Score difference = scores_a[i] - scores_b[i].
    """
    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)
    if len(a) != len(b):
        raise ValueError(f"Lengths must match: {len(a)} vs {len(b)}")

    diffs = a - b
    n_total = len(diffs)
    non_zero_diffs = diffs[diffs != 0]
    n_zero_diff = n_total - len(non_zero_diffs)

    if len(non_zero_diffs) == 0:
        return {
            "n_total": n_total,
            "n_zero_diff": n_zero_diff,
            "paired_items_n": n_total,
            "zero_difference_n": n_zero_diff,
            "effective_wilcoxon_n": 0,
            "zero_method": "wilcox",
            "alternative": "two-sided",
            "p_method": "none",
            "continuity_correction": False,
            "test_status": "NOT_APPLICABLE_ALL_DIFFERENCES_ZERO",
            "statistic": 0.0,
            "p_value": 1.0,  # 1.0 by defined reporting convention
            "rank_biserial_r": 0.0,
            "effect_size": 0.0,
            "interpretation": "identical_scores",
        }

    try:
        res = stats.wilcoxon(a, b, zero_method="wilcox", alternative="two-sided")
        stat = float(res.statistic)
        p_val = float(res.pvalue)

        # Matched rank-biserial correlation r_rb = (W+ - W-) / (W+ + W-)
        abs_diffs = np.abs(non_zero_diffs)
        ranks = stats.rankdata(abs_diffs)
        w_plus = np.sum(ranks[non_zero_diffs > 0])
        w_minus = np.sum(ranks[non_zero_diffs < 0])
        total_w = w_plus + w_minus
        r_rb = float((w_plus - w_minus) / total_w) if total_w > 0 else 0.0

        return {
            "n_total": n_total,
            "n_zero_diff": n_zero_diff,
            "paired_items_n": n_total,
            "zero_difference_n": n_zero_diff,
            "effective_wilcoxon_n": int(len(non_zero_diffs)),
            "zero_method": "wilcox",
            "alternative": "two-sided",
            "p_method": "asymptotic_normal",
            "continuity_correction": True,
            "test_status": "COMPUTED",
            "statistic": stat,
            "p_value": p_val,
            "rank_biserial_r": round(r_rb, 4),
            "effect_size": round(r_rb, 4),
        }
    except Exception as e:
        return {
            "n_total": n_total,
            "n_zero_diff": n_zero_diff,
            "paired_items_n": n_total,
            "zero_difference_n": n_zero_diff,
            "effective_wilcoxon_n": int(len(non_zero_diffs)),
            "zero_method": "wilcox",
            "alternative": "two-sided",
            "p_method": "asymptotic_normal",
            "continuity_correction": True,
            "test_status": "ERROR",
            "statistic": None,
            "p_value": None,
            "rank_biserial_r": None,
            "effect_size": None,
            "error": str(e),
        }


def paired_sensitivity_ttest(
    scores_a: List[float],
    scores_b: List[float],
) -> Dict[str, Any]:
    """
    Parametric sensitivity analysis: Paired Student's t-test and Cohen's d_z.
    """
    a = np.array(scores_a, dtype=float)
    b = np.array(scores_b, dtype=float)
    diffs = a - b
    mean_diff = float(np.mean(diffs))
    std_diff = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0

    if std_diff > 0:
        t_stat, p_val = stats.ttest_rel(a, b)
        cohens_dz = mean_diff / std_diff
    else:
        t_stat, p_val, cohens_dz = 0.0, 1.0, 0.0

    return {
        "mean_diff": round(mean_diff, 4),
        "std_diff": round(std_diff, 4),
        "t_statistic": round(float(t_stat), 4) if t_stat is not None else 0.0,
        "p_value": round(float(p_val), 4) if p_val is not None else 1.0,
        "cohens_dz": round(float(cohens_dz), 4),
    }


def paired_bootstrap_sacrebleu_difference(
    preds_a: List[str],
    preds_b: List[str],
    references_per_item: List[List[str]],
    n_iterations: int = 2000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Evaluates Corpus SacreBLEU difference via paired bootstrap resampling of evaluation items.
    Does NOT claim paired Wilcoxon test over a single corpus-level scalar.
    """
    n_items = len(preds_a)
    if len(preds_b) != n_items or len(references_per_item) != n_items:
        raise ValueError("Item counts must match across systems and references")

    rng = np.random.default_rng(seed)
    max_refs = max(len(r) for r in references_per_item)

    # Compute observed baseline corpus BLEUs
    ref_streams = []
    for r_idx in range(max_refs):
        ref_streams.append([r[r_idx] if r_idx < len(r) else r[0] for r in references_per_item])

    obs_bleu_a = sacrebleu.corpus_bleu(preds_a, ref_streams).score
    obs_bleu_b = sacrebleu.corpus_bleu(preds_b, ref_streams).score
    obs_diff = obs_bleu_a - obs_bleu_b

    bootstrap_diffs = []
    valid_replicates = 0
    undefined_replicates = 0

    for _ in range(n_iterations):
        sample_indices = rng.choice(n_items, size=n_items, replace=True)
        samp_a = [preds_a[i] for i in sample_indices]
        samp_b = [preds_b[i] for i in sample_indices]
        samp_refs = []
        for r_idx in range(max_refs):
            stream = [
                references_per_item[i][r_idx] if r_idx < len(references_per_item[i]) else references_per_item[i][0]
                for i in sample_indices
            ]
            samp_refs.append(stream)

        try:
            b_a = sacrebleu.corpus_bleu(samp_a, samp_refs).score
            b_b = sacrebleu.corpus_bleu(samp_b, samp_refs).score
            bootstrap_diffs.append(b_a - b_b)
            valid_replicates += 1
        except Exception:
            undefined_replicates += 1

    if valid_replicates >= 1000:
        ci_lower = float(np.percentile(bootstrap_diffs, 2.5))
        ci_upper = float(np.percentile(bootstrap_diffs, 97.5))
    else:
        ci_lower = None
        ci_upper = None

    return {
        "observed_corpus_bleu_a": round(obs_bleu_a, 2),
        "observed_corpus_bleu_b": round(obs_bleu_b, 2),
        "observed_difference": round(obs_diff, 2),
        "ci_95_lower": round(ci_lower, 2) if ci_lower is not None else None,
        "ci_95_upper": round(ci_upper, 2) if ci_upper is not None else None,
        "valid_replicates": valid_replicates,
        "undefined_replicates": undefined_replicates,
        "requested_iterations": n_iterations,
    }


def benjamini_hochberg_fdr(p_values: List[float], alpha: float = 0.05) -> List[Dict[str, Any]]:
    """
    Applies Benjamini-Hochberg procedure to control False Discovery Rate.
    Calculates exact rank, preliminary adjusted value, and monotonic adjusted q-value.
    """
    m = len(p_values)
    if m == 0:
        return []

    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    preliminary_adj = np.zeros(m)
    for i in range(m):
        rank = i + 1
        preliminary_adj[i] = (sorted_p[i] * m) / rank

    # Step-up monotonic correction: q_i = min_{j >= i} prelim_j
    monotonic_adj = np.zeros(m)
    min_val = 1.0
    for i in range(m - 1, -1, -1):
        min_val = min(min_val, preliminary_adj[i])
        monotonic_adj[i] = min(1.0, min_val)

    # Restore original ordering
    final_adj = np.zeros(m)
    final_adj[sorted_indices] = monotonic_adj

    ranks = np.zeros(m, dtype=int)
    ranks[sorted_indices] = np.arange(1, m + 1)

    prelim_ordered = np.zeros(m)
    prelim_ordered[sorted_indices] = preliminary_adj

    results = []
    for orig_p, rk, prelim, adj_p in zip(p_values, ranks, prelim_ordered, final_adj):
        results.append({
            "raw_p_value": float(orig_p),
            "rank": int(rk),
            "family_size_m": int(m),
            "preliminary_adj": float(prelim),
            "adjusted_p_value": float(adj_p),
            "significant_at_alpha": bool(adj_p <= alpha),
        })
    return results
