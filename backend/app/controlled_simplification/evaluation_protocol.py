"""
Evaluation protocol orchestrator for tier-matched, multi-reference, and Stage 24 cross-baseline benchmarking.
Computes SARI (Add/Keep/Delete), BLEU, FKGL reduction, monotonicity, and bootstrap confidence intervals.
"""

import math
import random
from typing import Dict, List, Tuple, Any
from app.datasets.external_english.benchmark.metrics import compute_sari, compute_bleu


def bootstrap_ci(
    scores_a: List[float],
    scores_b: List[float],
    n_resamples: int = 1000,
    confidence_level: float = 0.95
) -> Tuple[float, float, float, float]:
    """
    Computes paired mean difference, 95% bootstrap confidence intervals, and Cohen's d effect size.
    """
    if not scores_a or not scores_b or len(scores_a) != len(scores_b):
        return 0.0, 0.0, 0.0, 0.0

    differences = [a - b for a, b in zip(scores_a, scores_b)]
    n = len(differences)
    mean_diff = sum(differences) / float(n)

    # Standard deviation of differences
    variance = sum((d - mean_diff) ** 2 for d in differences) / float(max(1, n - 1))
    std_dev = math.sqrt(variance)
    cohen_d = mean_diff / std_dev if std_dev > 1e-6 else 0.0

    # Bootstrap resampling
    bootstrap_means = []
    for _ in range(n_resamples):
        sample = [random.choice(differences) for _ in range(n)]
        bootstrap_means.append(sum(sample) / float(n))

    bootstrap_means.sort()
    alpha = (1.0 - confidence_level) / 2.0
    low_idx = int(alpha * n_resamples)
    high_idx = int((1.0 - alpha) * n_resamples)

    ci_lower = bootstrap_means[min(low_idx, n_resamples - 1)]
    ci_upper = bootstrap_means[min(high_idx, n_resamples - 1)]

    return round(mean_diff, 2), round(ci_lower, 2), round(ci_upper, 2), round(cohen_d, 3)


class EvaluationOrchestrator:
    """
    Orchestrates tier-matched and cross-baseline evaluation protocols.
    """

    @staticmethod
    def evaluate_tier_matched(
        sources: List[str],
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates predictions against a single corresponding reference tier (e.g. Mild -> Mild).
        """
        sari_scores = []
        bleu_scores = []

        for src, pred, ref in zip(sources, predictions, references):
            s_mean, _, _, _ = compute_sari(src, pred, [ref])
            b_score = compute_bleu(pred, [ref])
            sari_scores.append(s_mean)
            bleu_scores.append(b_score)

        avg_sari = sum(sari_scores) / max(1, len(sari_scores))
        avg_bleu = sum(bleu_scores) / max(1, len(bleu_scores))

        return {
            "sample_count": len(sources),
            "sari": round(avg_sari, 2),
            "corpus_bleu": round(avg_bleu, 2)
        }

    @staticmethod
    def evaluate_multi_reference(
        sources: List[str],
        predictions: List[str],
        all_references: List[List[str]]
    ) -> Dict[str, Any]:
        """
        Evaluates predictions against all available reference tiers (Mild + Mod + Strong).
        """
        sari_scores = []
        bleu_scores = []

        for src, pred, refs in zip(sources, predictions, all_references):
            s_mean, _, _, _ = compute_sari(src, pred, refs)
            b_score = compute_bleu(pred, refs)
            sari_scores.append(s_mean)
            bleu_scores.append(b_score)

        avg_sari = sum(sari_scores) / max(1, len(sari_scores))
        avg_bleu = sum(bleu_scores) / max(1, len(bleu_scores))

        return {
            "sample_count": len(sources),
            "sari": round(avg_sari, 2),
            "corpus_bleu": round(avg_bleu, 2)
        }
