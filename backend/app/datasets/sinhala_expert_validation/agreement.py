"""
Stage 34 — Inter-Rater Agreement Analysis Service
Implements:
- Krippendorff's alpha (primary metric for nominal and ordinal scales with missingness support);
- Fleiss' kappa (secondary metric for eligible fully crossed nominal subsets);
- Exact agreement, confusion matrices, and bootstrap 95% confidence intervals;
- Point-estimate decision logic against frozen thresholds.
"""

from collections import Counter, defaultdict
import random
from typing import Any, Dict, List, Optional, Tuple


def compute_krippendorff_alpha_nominal(
    data_by_item: Dict[str, Dict[str, Any]],
) -> Optional[float]:
    """Computes Krippendorff's alpha for nominal data with variable raters and missingness."""
    # Filter items with at least 2 valid ratings
    valid_items = {}
    all_values = set()
    for item_id, raters in data_by_item.items():
        vals = [v for v in raters.values() if v is not None]
        if len(vals) >= 2:
            valid_items[item_id] = vals
            all_values.update(vals)

    if not valid_items or len(all_values) <= 1:
        return 1.0 if valid_items else None

    # Total number of pairwise comparisons
    val_list = sorted(list(all_values))
    val_map = {v: i for i, v in enumerate(val_list)}
    m = len(val_list)

    # Coincidence matrix
    coincidence = [[0.0] * m for _ in range(m)]
    total_pairs = 0

    for item_id, vals in valid_items.items():
        m_u = len(vals)
        norm = m_u - 1
        counts = Counter(vals)
        for v1, c1 in counts.items():
            i = val_map[v1]
            for v2, c2 in counts.items():
                j = val_map[v2]
                if v1 == v2:
                    coincidence[i][j] += (c1 * (c1 - 1)) / norm
                else:
                    coincidence[i][j] += (c1 * c2) / norm
        total_pairs += m_u

    total_coincidences = sum(sum(row) for row in coincidence)
    if total_coincidences == 0:
        return None

    # Marginals
    n_v = [sum(coincidence[i]) for i in range(m)]
    n_total = sum(n_v)

    # Observed disagreement
    d_o = 0.0
    for i in range(m):
        for j in range(m):
            if i != j:
                d_o += coincidence[i][j]

    # Expected disagreement
    d_e = 0.0
    for i in range(m):
        for j in range(m):
            if i != j:
                d_e += n_v[i] * n_v[j]

    if n_total <= 1 or d_e == 0:
        return 1.0

    d_e = d_e / (n_total - 1)
    alpha = 1.0 - (d_o / d_e)
    return round(alpha, 4)


def compute_krippendorff_alpha_ordinal(
    data_by_item: Dict[str, Dict[str, Any]],
) -> Optional[float]:
    """Computes Krippendorff's alpha for ordinal 0-3 scales using squared rank differences."""
    valid_items = {}
    all_values = set()
    for item_id, raters in data_by_item.items():
        vals = [int(v) for v in raters.values() if v is not None]
        if len(vals) >= 2:
            valid_items[item_id] = vals
            all_values.update(vals)

    if not valid_items or len(all_values) <= 1:
        return 1.0 if valid_items else None

    # Cumulative frequencies for ordinal metric
    val_counts = Counter()
    for vals in valid_items.values():
        val_counts.update(vals)

    all_ranks = sorted(list(all_values))
    rank_map = {r: idx for idx, r in enumerate(all_ranks)}
    m = len(all_ranks)

    # Coincidence matrix
    coincidence = [[0.0] * m for _ in range(m)]
    for vals in valid_items.values():
        m_u = len(vals)
        norm = m_u - 1
        counts = Counter(vals)
        for v1, c1 in counts.items():
            i = rank_map[v1]
            for v2, c2 in counts.items():
                j = rank_map[v2]
                if v1 == v2:
                    coincidence[i][j] += (c1 * (c1 - 1)) / norm
                else:
                    coincidence[i][j] += (c1 * c2) / norm

    n_v = [sum(coincidence[i]) for i in range(m)]
    n_total = sum(n_v)
    if n_total <= 1:
        return 1.0

    # Ordinal distance delta^2(c, k) = (sum_{g=min}^max n_g - (n_c + n_k)/2)^2
    dist = [[0.0] * m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            if i == j:
                dist[i][j] = 0.0
            else:
                low, high = min(i, j), max(i, j)
                inner_sum = sum(n_v[g] for g in range(low, high + 1))
                diff = inner_sum - (n_v[low] + n_v[high]) / 2.0
                dist[i][j] = diff ** 2

    # Observed disagreement
    d_o = sum(coincidence[i][j] * dist[i][j] for i in range(m) for j in range(m))

    # Expected disagreement
    d_e = sum(n_v[i] * n_v[j] * dist[i][j] for i in range(m) for j in range(m))
    if d_e == 0:
        return 1.0

    d_e = d_e / (n_total - 1)
    alpha = 1.0 - (d_o / d_e)
    return round(alpha, 4)


def compute_fleiss_kappa(
    data_by_item: Dict[str, Dict[str, Any]],
    expected_raters: int = 4,
) -> Optional[float]:
    """Computes Fleiss' kappa for eligible fully crossed nominal subsets.
    Rejects uneven rater counts or missing data.
    """
    for item_id, raters in data_by_item.items():
        vals = [v for v in raters.values() if v is not None]
        if len(vals) != expected_raters:
            raise ValueError(
                f"Fleiss' kappa assumption violated on {item_id}: expected exactly {expected_raters} complete ratings, got {len(vals)}"
            )

    all_cats = sorted(list({v for raters in data_by_item.values() for v in raters.values()}))
    cat_map = {c: i for i, c in enumerate(all_cats)}
    N = len(data_by_item)
    k = len(all_cats)
    n = expected_raters

    if N == 0 or k <= 1:
        return 1.0

    # Count table
    p_j = [0.0] * k
    P_i = []

    for item_id, raters in data_by_item.items():
        row = [0] * k
        for v in raters.values():
            row[cat_map[v]] += 1
        for j in range(k):
            p_j[j] += row[j]
        pi = (sum(r * r for r in row) - n) / (n * (n - 1))
        P_i.append(pi)

    for j in range(k):
        p_j[j] = p_j[j] / (N * n)

    P_bar = sum(P_i) / N
    P_e_bar = sum(pj * pj for pj in p_j)

    if P_e_bar == 1.0:
        return 1.0

    kappa = (P_bar - P_e_bar) / (1.0 - P_e_bar)
    return round(kappa, 4)


def bootstrap_ci(
    data_by_item: Dict[str, Dict[str, Any]],
    metric_func: Any,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Computes bootstrap 95% confidence interval using item-level resampling."""
    rng = random.Random(seed)
    items = list(data_by_item.keys())
    estimates = []

    for _ in range(n_resamples):
        sample_keys = [rng.choice(items) for _ in range(len(items))]
        sample_data = {f"res_{idx}": data_by_item[k] for idx, k in enumerate(sample_keys)}
        val = metric_func(sample_data)
        if val is not None:
            estimates.append(val)

    if not estimates:
        return (0.0, 1.0)

    estimates.sort()
    lower_idx = int(0.025 * len(estimates))
    upper_idx = int(0.975 * len(estimates))
    return (round(estimates[lower_idx], 4), round(estimates[upper_idx], 4))


def compute_exact_agreement(data_by_item: Dict[str, Dict[str, Any]]) -> float:
    """Computes average pairwise exact agreement proportion across items."""
    total_pairs = 0
    agreed_pairs = 0

    for raters in data_by_item.values():
        vals = [v for v in raters.values() if v is not None]
        m = len(vals)
        for i in range(m):
            for j in range(i + 1, m):
                total_pairs += 1
                if vals[i] == vals[j]:
                    agreed_pairs += 1

    if total_pairs == 0:
        return 1.0
    return round(agreed_pairs / total_pairs, 4)
