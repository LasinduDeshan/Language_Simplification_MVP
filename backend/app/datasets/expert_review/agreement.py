"""Agreement Metrics Service for Stage 27.

Calculates Cohen's kappa, quadratic weighted kappa, and ICC(3,1) within common fixed
reviewer pairs, and computes Krippendorff's alpha for corpus-wide aggregate agreement.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class AgreementService:
    """Computes inter-rater agreement statistics with proper panel handling."""

    @staticmethod
    def calculate_percent_agreement(rater_a: List[Any], rater_b: List[Any]) -> float:
        """Calculate raw percentage agreement (0.0 to 100.0)."""
        if not rater_a or len(rater_a) != len(rater_b):
            return 0.0
        matches = sum(1 for a, b in zip(rater_a, rater_b) if a == b)
        return round((matches / len(rater_a)) * 100.0, 2)

    @staticmethod
    def calculate_cohens_kappa(rater_a: List[Any], rater_b: List[Any]) -> Dict[str, Any]:
        """Calculate unweighted Cohen's kappa for nominal categories."""
        if not rater_a or len(rater_a) != len(rater_b):
            return {"kappa": 0.0}

        n = len(rater_a)
        categories = sorted(list(set(rater_a) | set(rater_b)))
        if len(categories) <= 1:
            return {"kappa": 1.0}  # Perfect consensus on single category

        cat_idx = {c: i for i, c in enumerate(categories)}
        k = len(categories)
        conf_matrix = np.zeros((k, k), dtype=float)

        for a, b in zip(rater_a, rater_b):
            conf_matrix[cat_idx[a], cat_idx[b]] += 1.0

        po = np.trace(conf_matrix) / n
        p_row = np.sum(conf_matrix, axis=1) / n
        p_col = np.sum(conf_matrix, axis=0) / n
        pe = np.sum(p_row * p_col)

        if pe >= 1.0:
            return {"kappa": 1.0}
        kappa = (po - pe) / (1.0 - pe)
        return {"kappa": round(float(kappa), 4)}

    @staticmethod
    def calculate_weighted_kappa(
        rater_a: List[int], rater_b: List[int], min_rating: int = 1, max_rating: int = 5
    ) -> Dict[str, Any]:
        """Calculate quadratic weighted Cohen's kappa for ordinal ratings."""
        if not rater_a or len(rater_a) != len(rater_b):
            return {"weighted_kappa": 0.0}

        n = len(rater_a)
        num_cats = max_rating - min_rating + 1
        conf_matrix = np.zeros((num_cats, num_cats), dtype=float)

        for a, b in zip(rater_a, rater_b):
            idx_a = max(0, min(num_cats - 1, a - min_rating))
            idx_b = max(0, min(num_cats - 1, b - min_rating))
            conf_matrix[idx_a, idx_b] += 1.0

        conf_matrix /= n

        # Quadratic weights: w_ij = (i - j)^2 / (k - 1)^2
        weights = np.zeros((num_cats, num_cats), dtype=float)
        denom = (num_cats - 1) ** 2
        for i in range(num_cats):
            for j in range(num_cats):
                weights[i, j] = ((i - j) ** 2) / denom

        r = np.sum(conf_matrix, axis=1)
        s = np.sum(conf_matrix, axis=0)
        expected = np.outer(r, s)

        po = np.sum(weights * conf_matrix)
        pe = np.sum(weights * expected)

        if pe <= 0.0:
            return {"weighted_kappa": 1.0}
        kappa_w = 1.0 - (po / pe)
        return {"weighted_kappa": round(float(kappa_w), 4)}

    @staticmethod
    def calculate_icc(
        ratings_matrix: Union[np.ndarray, List[List[float]]], form: str = "ICC(3,1)"
    ) -> Dict[str, Any]:
        """Calculate ICC(3,1) for two-way mixed effects, single rater, absolute agreement.
        
        ratings_matrix: array of shape (N, k) where N is items, k is raters (typically k=2).
        """
        arr = np.array(ratings_matrix, dtype=float)
        if arr.ndim != 2 or arr.shape[1] < 2:
            return {"icc_value": 0.0, "icc_form": form, "fixed_panel_assumed": True}

        n, k = arr.shape
        item_means = np.mean(arr, axis=1)
        rater_means = np.mean(arr, axis=0)
        grand_mean = np.mean(arr)

        ss_total = np.sum((arr - grand_mean) ** 2)
        ss_items = k * np.sum((item_means - grand_mean) ** 2)
        ss_raters = n * np.sum((rater_means - grand_mean) ** 2)
        ss_error = ss_total - ss_items - ss_raters

        ms_items = ss_items / (n - 1) if n > 1 else 0.0
        ms_error = ss_error / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0.0

        if ms_items + (k - 1) * ms_error == 0:
            icc = 0.0
        else:
            icc = (ms_items - ms_error) / (ms_items + (k - 1) * ms_error)

        return {
            "icc_value": round(float(icc), 4),
            "icc_form": form,
            "fixed_panel_assumed": True,
            "number_of_reviewers": k,
        }

    @staticmethod
    def calculate_krippendorff_alpha(
        matrix: List[List[Optional[Any]]], level_of_measurement: str = "nominal"
    ) -> Dict[str, Any]:
        """Calculate Krippendorff's alpha for nominal data supporting multiple/varying raters."""
        valid_items = [row for row in matrix if len([x for x in row if x is not None]) >= 2]
        if not valid_items:
            return {"alpha": 0.0}

        categories = sorted(list({x for row in valid_items for x in row if x is not None}))
        if len(categories) <= 1:
            return {"alpha": 1.0}

        n_v = len(categories)
        cat_map = {c: i for i, c in enumerate(categories)}

        coincidence = np.zeros((n_v, n_v), dtype=float)
        total_pairs = 0.0

        for row in valid_items:
            vals = [x for x in row if x is not None]
            m = len(vals)
            if m < 2:
                continue
            for i in range(m):
                for j in range(m):
                    if i != j:
                        c_i = cat_map[vals[i]]
                        c_j = cat_map[vals[j]]
                        coincidence[c_i, c_j] += 1.0 / (m - 1)
                        total_pairs += 1.0 / (m - 1)

        if total_pairs == 0:
            return {"alpha": 0.0}

        d_o = np.sum(coincidence) - np.trace(coincidence)
        d_o /= total_pairs

        margins = np.sum(coincidence, axis=1) / total_pairs
        d_e = 1.0 - np.sum(margins ** 2)

        if d_e == 0:
            return {"alpha": 1.0}
        alpha = 1.0 - (d_o / d_e)
        return {"alpha": round(float(alpha), 4)}

    def calculate_batch_agreement(
        self,
        batch_id: str,
        reviewer_panel_id: str,
        reviewer_a_id: str,
        reviewer_b_id: str,
        submissions_a: List[Any],
        submissions_b: List[Any],
    ) -> Dict[str, Any]:
        """Calculates comprehensive agreement statistics for a fixed reviewer pair batch."""
        n_items = len(submissions_a)
        if n_items == 0 or len(submissions_b) != n_items:
            return {
                "batch_id": batch_id,
                "reviewer_panel_id": reviewer_panel_id,
                "reviewer_ids": [reviewer_a_id, reviewer_b_id],
                "records_reviewed": 0,
                "error": "Mismatched submission lengths or empty batch",
            }

        tax_a = [s.taxonomy_class.value for s in submissions_a]
        tax_b = [s.taxonomy_class.value for s in submissions_b]
        tax_kappa = self.calculate_cohens_kappa(tax_a, tax_b)["kappa"]
        tax_po = self.calculate_percent_agreement(tax_a, tax_b)

        crit_a = [int(s.critical_checks.has_critical_failure()) for s in submissions_a]
        crit_b = [int(s.critical_checks.has_critical_failure()) for s in submissions_b]
        crit_kappa = self.calculate_cohens_kappa(crit_a, crit_b)["kappa"]

        meaning_a = [s.ratings.meaning_preservation for s in submissions_a]
        meaning_b = [s.ratings.meaning_preservation for s in submissions_b]
        meaning_weighted_kappa = self.calculate_weighted_kappa(meaning_a, meaning_b)["weighted_kappa"]

        age_a = [s.ratings.age_appropriateness for s in submissions_a]
        age_b = [s.ratings.age_appropriateness for s in submissions_b]
        age_weighted_kappa = self.calculate_weighted_kappa(age_a, age_b)["weighted_kappa"]

        avg_ratings_matrix = np.column_stack([
            [s.ratings.average_score() for s in submissions_a],
            [s.ratings.average_score() for s in submissions_b],
        ])
        icc_res = self.calculate_icc(avg_ratings_matrix, form="ICC(3,1)")

        return {
            "batch_id": batch_id,
            "reviewer_panel_id": reviewer_panel_id,
            "reviewer_ids": [reviewer_a_id, reviewer_b_id],
            "records_reviewed": n_items,
            "agreement_method": "Cohen_Kappa_and_ICC3_1_fixed_panel",
            "agreement_denominator": n_items,
            "taxonomy_cohens_kappa": tax_kappa,
            "taxonomy_percent_agreement": tax_po,
            "critical_checks_cohens_kappa": crit_kappa,
            "meaning_preservation_weighted_kappa": meaning_weighted_kappa,
            "age_appropriateness_weighted_kappa": age_weighted_kappa,
            "icc_3_1_average_ratings": icc_res["icc_value"],
        }


# Alias for backward and testing compatibility
AgreementCalculator = AgreementService
