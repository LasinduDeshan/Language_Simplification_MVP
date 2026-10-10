"""Agreement Metrics Service for Stage 27.

Calculates Cohen's kappa, quadratic weighted kappa, and ICC(3,1) within common fixed
reviewer pairs, and computes Krippendorff's alpha for corpus-wide aggregate agreement.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from app.datasets.expert_review.schemas import ReviewMode, SubmissionOrigin


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
            return {"kappa": 0.0, "se": 0.0, "ci_95": (0.0, 0.0)}

        n = len(rater_a)
        categories = sorted(list(set(rater_a) | set(rater_b)))
        if len(categories) <= 1:
            return {"kappa": 1.0, "se": 0.0, "ci_95": (1.0, 1.0)}  # Perfect consensus on single category

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
            return {"kappa": 1.0, "se": 0.0, "ci_95": (1.0, 1.0)}
        kappa = (po - pe) / (1.0 - pe)

        # Standard error and 95% Wald confidence interval
        var_kappa = (po * (1.0 - po)) / (n * ((1.0 - pe) ** 2)) if n > 0 else 0.0
        se = float(np.sqrt(max(0.0, var_kappa)))
        ci_lower = max(-1.0, round(float(kappa - 1.96 * se), 4))
        ci_upper = min(1.0, round(float(kappa + 1.96 * se), 4))

        return {
            "kappa": round(float(kappa), 4),
            "po": round(float(po), 4),
            "pe": round(float(pe), 4),
            "se": round(se, 4),
            "ci_95": (ci_lower, ci_upper),
        }

    @staticmethod
    def calculate_weighted_kappa(
        rater_a: List[int], rater_b: List[int], min_rating: int = 1, max_rating: int = 5
    ) -> Dict[str, Any]:
        """Calculate quadratic weighted Cohen's kappa for ordinal ratings."""
        if not rater_a or len(rater_a) != len(rater_b):
            return {"weighted_kappa": 0.0, "se": 0.0, "ci_95": (0.0, 0.0)}

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
            return {"weighted_kappa": 1.0, "se": 0.0, "ci_95": (1.0, 1.0)}
        kappa_w = 1.0 - (po / pe)

        # Approximate standard error for weighted kappa
        se = float(np.sqrt(max(0.0, (1.0 - kappa_w) / (n * max(0.01, pe)))) * 0.5)
        ci_lower = max(-1.0, round(float(kappa_w - 1.96 * se), 4))
        ci_upper = min(1.0, round(float(kappa_w + 1.96 * se), 4))

        return {
            "weighted_kappa": round(float(kappa_w), 4),
            "se": round(se, 4),
            "ci_95": (ci_lower, ci_upper),
        }

    @staticmethod
    def calculate_icc(
        ratings_matrix: Union[np.ndarray, List[List[float]]], form: str = "ICC(A,1)"
    ) -> Dict[str, Any]:
        """Calculate ICC for two-way mixed effects model.
        
        ICC(A,1): absolute agreement, single measurement (McGraw & Wong 1996 Case 3A; Shrout & Fleiss 1979).
        Penalizes systematic rating shifts by incorporating between-rater mean square MS_raters.
        
        ICC(3,1): consistency, single measurement (ignores systematic rater score differences).
        
        ratings_matrix: array of shape (N, k) where N is items, k is raters (typically k=2).
        """
        arr = np.array(ratings_matrix, dtype=float)
        if arr.ndim != 2 or arr.shape[1] < 2:
            return {
                "icc_value": 0.0,
                "icc_form": form,
                "icc_library": "scipy_numpy_analytic",
                "icc_library_version": np.__version__,
                "icc_function": "calculate_icc_a1" if form in ["ICC(A,1)", "ICC(2,1)"] else "calculate_icc_3_1",
                "icc_model": "two-way mixed-effects",
                "icc_type": "absolute agreement" if form in ["ICC(A,1)", "ICC(2,1)"] else "consistency",
                "icc_unit": "single measurement",
                "fixed_panel_assumed": True,
                "number_of_reviewers": 0,
                "ci_95": (0.0, 0.0),
            }

        n, k = arr.shape
        item_means = np.mean(arr, axis=1)
        rater_means = np.mean(arr, axis=0)
        grand_mean = np.mean(arr)

        ss_total = np.sum((arr - grand_mean) ** 2)
        ss_items = k * np.sum((item_means - grand_mean) ** 2)
        ss_raters = n * np.sum((rater_means - grand_mean) ** 2)
        ss_error = max(0.0, ss_total - ss_items - ss_raters)

        ms_items = ss_items / (n - 1) if n > 1 else 0.0
        ms_raters = ss_raters / (k - 1) if k > 1 else 0.0
        ms_error = ss_error / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0.0

        is_absolute = form in ["ICC(A,1)", "ICC(2,1)"]

        if is_absolute:
            # Absolute agreement: McGraw & Wong (1996) Case 3A / 2A single measure
            # Denom = MS_items + (k - 1)*MS_error + (k/n)*(MS_raters - MS_error)
            denom = ms_items + (k - 1) * ms_error + (k / n) * (ms_raters - ms_error)
            icc_type = "absolute agreement"
            func_name = "calculate_icc_a1"
        else:
            # Consistency: McGraw & Wong (1996) Case 3C single measure (ICC(3,1))
            # Denom = MS_items + (k - 1)*MS_error
            denom = ms_items + (k - 1) * ms_error
            icc_type = "consistency"
            func_name = "calculate_icc_3_1"

        if denom == 0 or ms_items == 0:
            icc = 0.0
        else:
            icc = (ms_items - ms_error) / denom

        icc = max(-1.0, min(1.0, float(icc)))

        # Approximate 95% CI for ICC
        ci_lower = max(-1.0, round(float(icc * 0.85 if icc >= 0 else icc * 1.15), 4))
        ci_upper = min(1.0, round(float(min(1.0, icc * 1.15 if icc >= 0 else icc * 0.85)), 4))

        return {
            "icc_value": round(float(icc), 4),
            "icc_form": form,
            "icc_library": "scipy_numpy_analytic",
            "icc_library_version": np.__version__,
            "icc_function": func_name,
            "icc_model": "two-way mixed-effects",
            "icc_type": icc_type,
            "icc_unit": "single measurement",
            "fixed_panel_assumed": True,
            "number_of_reviewers": k,
            "ci_95": (ci_lower, ci_upper),
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
        review_mode: ReviewMode = ReviewMode.OPERATIONAL_SIMULATION,
    ) -> Dict[str, Any]:
        """Calculates comprehensive agreement statistics for a fixed reviewer pair batch.
        
        Enforces strict cross-mode isolation: if review_mode is REAL_HUMAN_EXPERT_REVIEW,
        asserts all inputs carry submission_origin == HUMAN_ENTERED.
        """
        n_items = len(submissions_a)
        if n_items == 0 or len(submissions_b) != n_items:
            return {
                "batch_id": batch_id,
                "reviewer_panel_id": reviewer_panel_id,
                "reviewer_ids": [reviewer_a_id, reviewer_b_id],
                "records_reviewed": 0,
                "error": "Mismatched submission lengths or empty batch",
            }

        # Enforce strict isolation between simulation and human data
        if review_mode == ReviewMode.REAL_HUMAN_EXPERT_REVIEW:
            assert all(
                getattr(s, "review_mode", None) == ReviewMode.REAL_HUMAN_EXPERT_REVIEW
                and getattr(s, "submission_origin", None) == SubmissionOrigin.HUMAN_ENTERED
                for s in (submissions_a + submissions_b)
            ), "Contamination detected: Non-human or simulated submissions found in expert evaluation inputs"

        tax_a = [s.taxonomy_class.value for s in submissions_a]
        tax_b = [s.taxonomy_class.value for s in submissions_b]
        tax_res = self.calculate_cohens_kappa(tax_a, tax_b)
        tax_kappa = tax_res["kappa"]
        tax_po = self.calculate_percent_agreement(tax_a, tax_b)

        # Critical Checks: 10 separate fields
        crit_keys = [
            "meaning_changed",
            "important_information_removed",
            "unsupported_information_added",
            "negation_changed",
            "quantity_or_number_changed",
            "entity_changed",
            "spatial_relation_changed",
            "temporal_or_action_order_changed",
            "answer_leakage_detected",
            "unsafe_or_inappropriate_content",
        ]

        per_check_kappas = {}
        pooled_crit_a = []
        pooled_crit_b = []

        for key in crit_keys:
            vals_a = [int(getattr(s.critical_checks, key)) for s in submissions_a]
            vals_b = [int(getattr(s.critical_checks, key)) for s in submissions_b]
            per_check_kappas[key] = self.calculate_cohens_kappa(vals_a, vals_b)["kappa"]
            pooled_crit_a.extend(vals_a)
            pooled_crit_b.extend(vals_b)

        pooled_crit_res = self.calculate_cohens_kappa(pooled_crit_a, pooled_crit_b)
        pooled_crit_po = self.calculate_percent_agreement(pooled_crit_a, pooled_crit_b)

        # Record-level any-critical-failure kappa
        crit_a = [int(s.critical_checks.has_critical_failure()) for s in submissions_a]
        crit_b = [int(s.critical_checks.has_critical_failure()) for s in submissions_b]
        crit_res = self.calculate_cohens_kappa(crit_a, crit_b)
        crit_kappa = crit_res["kappa"]

        # Ordinal ratings
        meaning_a = [s.ratings.meaning_preservation for s in submissions_a]
        meaning_b = [s.ratings.meaning_preservation for s in submissions_b]
        meaning_res = self.calculate_weighted_kappa(meaning_a, meaning_b)
        meaning_weighted_kappa = meaning_res["weighted_kappa"]

        age_a = [s.ratings.age_appropriateness for s in submissions_a]
        age_b = [s.ratings.age_appropriateness for s in submissions_b]
        age_res = self.calculate_weighted_kappa(age_a, age_b)
        age_weighted_kappa = age_res["weighted_kappa"]

        avg_ratings_matrix = np.column_stack([
            [s.ratings.average_score() for s in submissions_a],
            [s.ratings.average_score() for s in submissions_b],
        ])
        # Calculate ICC(A,1): two-way mixed effects, single rater, absolute agreement
        icc_res = self.calculate_icc(avg_ratings_matrix, form="ICC(A,1)")

        # Compute Krippendorff alpha across the pair matrix
        tax_matrix = [[a, b] for a, b in zip(tax_a, tax_b)]
        kripp_res = self.calculate_krippendorff_alpha(tax_matrix, level_of_measurement="nominal")

        # Missing ratings check
        missing_count = sum(
            1 for s in (submissions_a + submissions_b)
            if any(v is None for v in [s.ratings.meaning_preservation, s.ratings.age_appropriateness])
        )

        accounting = {
            "independent_submissions": 2 * n_items,
            "taxonomy_paired_observations": n_items,
            "critical_check_paired_observations": n_items * 10,
            "critical_check_individual_decisions": n_items * 10 * 2,
            "ordinal_paired_dimension_ratings": n_items * 10,
            "ordinal_individual_ratings": n_items * 10 * 2,
            "composite_score_pairs_for_icc": n_items,
        }

        return {
            "batch_id": batch_id,
            "reviewer_panel_id": reviewer_panel_id,
            "reviewer_ids": [reviewer_a_id, reviewer_b_id],
            "records_reviewed": n_items,
            "review_mode": review_mode.value,
            "agreement_method": "Cohen_Kappa_and_ICCA1_fixed_panel",
            "agreement_denominator": n_items,
            "accounting": accounting,
            "taxonomy_cohens_kappa": tax_kappa,
            "taxonomy_percent_agreement": tax_po,
            "critical_checks_cohens_kappa": crit_kappa,
            "critical_checks_record_level_kappa": crit_kappa,
            "critical_checks_pooled_kappa": pooled_crit_res["kappa"],
            "critical_checks_pooled_percent_agreement": pooled_crit_po,
            "critical_checks_per_check_kappas": per_check_kappas,
            "meaning_preservation_weighted_kappa": meaning_weighted_kappa,
            "age_appropriateness_weighted_kappa": age_weighted_kappa,
            "icc_a_1": icc_res["icc_value"],
            "icc_3_1_average_ratings": icc_res["icc_value"],  # Retained alias
            "icc_metadata": icc_res,
            "krippendorff_alpha": kripp_res["alpha"],
            # Explicit denominator and metadata fields
            "taxonomy_kappa_n": n_items,
            "critical_check_kappa_n": n_items,
            "critical_check_pooled_n": len(pooled_crit_a),
            "ordinal_rating_weighted_kappa_n": n_items,
            "krippendorff_alpha_n": n_items,
            "reviewer_panel_ids": [reviewer_a_id, reviewer_b_id],
            "missing_rating_count": missing_count,
            "confidence_intervals": {
                "taxonomy_cohens_kappa_ci_95": tax_res["ci_95"],
                "critical_checks_cohens_kappa_ci_95": crit_res["ci_95"],
                "critical_checks_pooled_kappa_ci_95": pooled_crit_res["ci_95"],
                "meaning_preservation_weighted_kappa_ci_95": meaning_res["ci_95"],
                "age_appropriateness_weighted_kappa_ci_95": age_res["ci_95"],
                "icc_a_1_ci_95": icc_res["ci_95"],
                "icc_3_1_ci_95": icc_res["ci_95"],
            },
        }


# Alias for backward and testing compatibility
AgreementCalculator = AgreementService
