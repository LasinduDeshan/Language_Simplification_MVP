"""Tests for inter-rater agreement statistics within fixed panels and across varying panels."""
import pytest
from app.datasets.expert_review.agreement import AgreementCalculator


@pytest.fixture
def calc():
    return AgreementCalculator()


def test_percent_agreement(calc):
    """Test exact percentage agreement calculation."""
    r1 = ["A", "B", "C", "D"]
    r2 = ["A", "B", "C", "E"]
    pct = calc.calculate_percent_agreement(r1, r2)
    assert pct == 75.0


def test_cohens_kappa_perfect_agreement(calc):
    """Perfect agreement yields kappa = 1.0."""
    r1 = ["yes", "no", "yes", "no", "yes"]
    r2 = ["yes", "no", "yes", "no", "yes"]
    res = calc.calculate_cohens_kappa(r1, r2)
    assert res["kappa"] == 1.0


def test_cohens_kappa_chance_agreement(calc):
    """Zero agreement beyond chance yields lower kappa."""
    r1 = ["yes", "yes", "no", "no"]
    r2 = ["no", "no", "yes", "yes"]
    res = calc.calculate_cohens_kappa(r1, r2)
    assert res["kappa"] < 0.0


def test_weighted_kappa_ordinal(calc):
    """Quadratic weighted kappa penalizes distance squared."""
    # Near ratings (4 vs 5) should yield high weighted kappa
    r1 = [1, 2, 3, 4, 5, 4, 3, 2, 1]
    r2 = [1, 2, 3, 5, 5, 4, 3, 2, 2]
    res = calc.calculate_weighted_kappa(r1, r2)
    assert res["weighted_kappa"] > 0.80


def test_icc_3_1_fixed_panel(calc):
    """Calculates ICC(3,1) two-way mixed effects, single rater, absolute agreement within fixed panels."""
    ratings_matrix = [
        [4.0, 4.0],
        [5.0, 5.0],
        [2.0, 2.0],
        [3.0, 3.0],
        [4.0, 4.0],
        [1.0, 1.0],
    ]
    res = calc.calculate_icc(ratings_matrix, form="ICC(3,1)")
    assert res["icc_form"] == "ICC(3,1)"
    assert res["icc_value"] > 0.90
    assert res["fixed_panel_assumed"] is True


def test_krippendorff_alpha_nominal(calc):
    """Calculates Krippendorff's alpha for nominal data across varying panels."""
    # Perfect nominal agreement across raters
    data = [
        ["A", "A", "A"],
        ["B", "B", "B"],
        ["C", "C", "C"],
        ["D", "D", "D"],
    ]
    res = calc.calculate_krippendorff_alpha(data, level_of_measurement="nominal")
    assert res["alpha"] == 1.0


def test_batch_agreement_denominators_and_confidence_intervals(calc):
    """Verifies explicit agreement denominators, panel IDs, and 95% confidence intervals."""
    from app.datasets.expert_review.schemas import (
        RecordReviewSubmission, TaxonomyClass, DimensionRatings, CriticalFailureFlags, WorkflowFlags
    )

    subs_a = [
        RecordReviewSubmission(
            submission_id=f"SUB-A-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-01",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(meaning_preservation=4, age_appropriateness=4),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-a-{i}",
        )
        for i in range(10)
    ]

    subs_b = [
        RecordReviewSubmission(
            submission_id=f"SUB-B-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-02",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION if i != 0 else TaxonomyClass.INSTRUCTION_REPHRASING,
            ratings=DimensionRatings(meaning_preservation=4 if i != 1 else 3, age_appropriateness=4),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-b-{i}",
        )
        for i in range(10)
    ]

    res = calc.calculate_batch_agreement(
        batch_id="BATCH-01",
        reviewer_panel_id="PANEL-01",
        reviewer_a_id="REV-01",
        reviewer_b_id="REV-02",
        submissions_a=subs_a,
        submissions_b=subs_b,
    )

    assert res["taxonomy_kappa_n"] == 10
    assert res["critical_check_kappa_n"] == 10
    assert res["ordinal_rating_weighted_kappa_n"] == 10
    assert res["krippendorff_alpha_n"] == 10
    assert res["reviewer_panel_ids"] == ["REV-01", "REV-02"]
    assert res["missing_rating_count"] == 0
    assert "confidence_intervals" in res
    assert "taxonomy_cohens_kappa_ci_95" in res["confidence_intervals"]
    assert "critical_checks_cohens_kappa_ci_95" in res["confidence_intervals"]
    assert "critical_checks_pooled_kappa_ci_95" in res["confidence_intervals"]
    assert "meaning_preservation_weighted_kappa_ci_95" in res["confidence_intervals"]
    assert "age_appropriateness_weighted_kappa_ci_95" in res["confidence_intervals"]
    assert "icc_a_1_ci_95" in res["confidence_intervals"]
    assert "icc_3_1_ci_95" in res["confidence_intervals"]
    assert -1.0 <= res["krippendorff_alpha"] <= 1.0

    # Verify accounting
    acc = res["accounting"]
    assert acc["independent_submissions"] == 20
    assert acc["taxonomy_paired_observations"] == 10
    assert acc["critical_check_paired_observations"] == 100
    assert acc["critical_check_individual_decisions"] == 200
    assert acc["ordinal_paired_dimension_ratings"] == 100
    assert acc["ordinal_individual_ratings"] == 200
    assert acc["composite_score_pairs_for_icc"] == 10


def test_icc_a1_absolute_agreement_penalizes_systematic_shift(calc):
    """ICC(A,1) absolute agreement must penalize systematic scoring shifts between raters."""
    # Rater B scores every item exactly 1 point higher than Rater A
    # Consistency ICC(3,1) is 1.0 (perfect correlation), but Absolute Agreement ICC(A,1) is lower
    shifted_matrix = [
        [1.0, 2.0],
        [2.0, 3.0],
        [3.0, 4.0],
        [4.0, 5.0],
        [2.0, 3.0],
        [3.0, 4.0],
    ]
    res_a1 = calc.calculate_icc(shifted_matrix, form="ICC(A,1)")
    res_31 = calc.calculate_icc(shifted_matrix, form="ICC(3,1)")

    assert res_a1["icc_form"] == "ICC(A,1)"
    assert res_a1["icc_model"] == "two-way mixed-effects"
    assert res_a1["icc_type"] == "absolute agreement"
    assert res_a1["icc_unit"] == "single measurement"
    assert res_a1["numpy_version"] is not None
    assert res_a1["scipy_version"] is not None
    assert res_a1["agreement_module_version"] == "1.2.0"
    assert res_a1["implementation_hash"] is not None

    # Consistency is perfect (1.0) because rankings are identical
    assert res_31["icc_value"] == 1.0
    # Absolute agreement is penalized (< 1.0) because rater B gave systematically higher scores
    assert res_a1["icc_value"] < 0.90


def test_mode_isolation_guard(calc):
    """Enforces strict isolation: simulated reviews cannot enter human evaluation."""
    from app.datasets.expert_review.schemas import (
        RecordReviewSubmission, TaxonomyClass, DimensionRatings, CriticalFailureFlags,
        WorkflowFlags, ReviewMode, SubmissionOrigin
    )

    sim_sub_a = [
        RecordReviewSubmission(
            submission_id="SUB-SIM-A",
            item_id="REC-1",
            reviewer_id="REV-01",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash="hash-1",
            submission_origin=SubmissionOrigin.SCRIPT_GENERATED,
            review_mode=ReviewMode.OPERATIONAL_SIMULATION,
        )
    ]
    sim_sub_b = [
        RecordReviewSubmission(
            submission_id="SUB-SIM-B",
            item_id="REC-1",
            reviewer_id="REV-02",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash="hash-2",
            submission_origin=SubmissionOrigin.SCRIPT_GENERATED,
            review_mode=ReviewMode.OPERATIONAL_SIMULATION,
        )
    ]

    # Passing simulated submissions into REAL_HUMAN_EXPERT_REVIEW must raise AssertionError
    with pytest.raises(AssertionError, match="Contamination detected"):
        calc.calculate_batch_agreement(
            batch_id="BATCH-01",
            reviewer_panel_id="PANEL-01",
            reviewer_a_id="REV-01",
            reviewer_b_id="REV-02",
            submissions_a=sim_sub_a,
            submissions_b=sim_sub_b,
            review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        )


def test_stratified_bootstrap_ci_execution_and_metadata(calc):
    """Verifies that stratified bootstrap preserves record pairs, uses >= 2000 iterations, and logs metadata."""
    from app.datasets.expert_review.schemas import (
        RecordReviewSubmission, TaxonomyClass, DimensionRatings, CriticalFailureFlags,
        WorkflowFlags, ReviewMode, SubmissionOrigin
    )

    subs_a = [
        RecordReviewSubmission(
            submission_id=f"SUB-A-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-01",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(meaning_preservation=4, age_appropriateness=4 if i % 2 == 0 else 5),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-a-{i}",
            submission_origin=SubmissionOrigin.HUMAN_ENTERED,
            review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        )
        for i in range(20)
    ]

    subs_b = [
        RecordReviewSubmission(
            submission_id=f"SUB-B-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-02",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION if i % 4 != 0 else TaxonomyClass.INSTRUCTION_REPHRASING,
            ratings=DimensionRatings(
                meaning_preservation=4 if i % 3 != 0 else 3,
                age_appropriateness=4 if i % 2 == 0 else 5,
            ),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-b-{i}",
            submission_origin=SubmissionOrigin.HUMAN_ENTERED,
            review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        )
        for i in range(20)
    ]

    strata = ["simplification_pair"] * 14 + ["lexicon_entry"] * 4 + ["adaptation_activity"] * 2

    res = calc.calculate_batch_agreement(
        batch_id="BATCH-01",
        reviewer_panel_id="PANEL-01",
        reviewer_a_id="REV-01",
        reviewer_b_id="REV-02",
        submissions_a=subs_a,
        submissions_b=subs_b,
        review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        strata=strata,
        bootstrap_iterations=2000,
        random_seed=42,
    )

    ci = res["confidence_intervals"]
    assert ci["method"] == "stratified_bootstrap"
    assert ci["requested_iterations"] == 2000
    assert ci["minimum_valid_iterations"] == 1000
    assert ci["iterations"] == 2000
    assert ci["random_seed"] == 42
    assert ci["sampling_unit"] == "complete_record"
    assert ci["strata"] == "record_type"
    assert ci["confidence_level"] == 0.95
    assert ci["numpy_version"] is not None
    assert ci["scipy_version"] is not None
    assert ci["agreement_module_version"] == "1.2.0"
    assert ci["algorithm"] == "SHA-256"
    assert len(ci["implementation_hash"]) == 64

    # Undefined replicates tracking
    assert "valid_iterations" in ci
    assert "undefined_iterations" in ci
    assert "undefined_reason_counts" in ci
    assert ci["undefined_reason_counts"]["no_positive_critical_flags"] == 2000

    # In this dataset with zero critical failures, critical checks kappa is undefined / unavailable
    assert ci["critical_checks_cohens_kappa_ci_95"] == "unavailable"

    # Other metrics with variance produce valid confidence intervals
    for key in [
        "taxonomy_cohens_kappa_ci_95",
        "meaning_preservation_weighted_kappa_ci_95",
        "age_appropriateness_weighted_kappa_ci_95",
        "icc_a_1_ci_95",
        "icc_3_1_ci_95",
    ]:
        lo, hi = ci[key]
        assert -1.0 <= lo <= 1.0
        assert -1.0 <= hi <= 1.0
        assert lo <= hi


def test_sha256_implementation_hash_is_64_hex_chars(calc):
    """Verifies that the implementation hash is exactly 64 hexadecimal characters computed from SHA-256."""
    from app.datasets.expert_review.agreement import IMPLEMENTATION_HASH, IMPLEMENTATION_INFO
    assert IMPLEMENTATION_INFO["algorithm"] == "SHA-256"
    assert len(IMPLEMENTATION_INFO["implementation_hash"]) == 64
    assert len(IMPLEMENTATION_HASH) == 64
    assert all(c in "0123456789abcdef" for c in IMPLEMENTATION_HASH)


def test_bootstrap_handles_undefined_replicates_without_zero_or_one_coercion(calc):
    """Verifies that undefined replicates are not converted to 0 or 1, and report 'unavailable' if insufficient."""
    from app.datasets.expert_review.schemas import (
        RecordReviewSubmission, TaxonomyClass, DimensionRatings, CriticalFailureFlags,
        WorkflowFlags, ReviewMode, SubmissionOrigin
    )

    # All items identical: single taxonomy class, no positive critical flags
    subs_a = [
        RecordReviewSubmission(
            submission_id=f"SUB-A-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-01",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(meaning_preservation=4, age_appropriateness=4),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-a-{i}",
            submission_origin=SubmissionOrigin.HUMAN_ENTERED,
            review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        )
        for i in range(10)
    ]
    subs_b = [
        RecordReviewSubmission(
            submission_id=f"SUB-B-{i}",
            item_id=f"REC-{i}",
            reviewer_id="REV-02",
            batch_id="BATCH-01",
            taxonomy_class=TaxonomyClass.TEXT_SIMPLIFICATION,
            ratings=DimensionRatings(meaning_preservation=4, age_appropriateness=4),
            critical_checks=CriticalFailureFlags(),
            workflow_flags=WorkflowFlags(),
            submission_hash=f"h-b-{i}",
            submission_origin=SubmissionOrigin.HUMAN_ENTERED,
            review_mode=ReviewMode.REAL_HUMAN_EXPERT_REVIEW,
        )
        for i in range(10)
    ]

    boot_res = calc.calculate_stratified_bootstrap_ci(
        subs_a,
        subs_b,
        iterations=500,
        minimum_valid_iterations=250,
    )

    assert boot_res["requested_iterations"] == 500
    assert boot_res["minimum_valid_iterations"] == 250
    # Because there is only 1 class, every replicate is undefined (not coerced to 1.0 or 0.0)
    assert boot_res["undefined_reason_counts"]["single_taxonomy_class"] == 500
    assert boot_res["undefined_reason_counts"]["no_positive_critical_flags"] == 500
    assert boot_res["taxonomy_cohens_kappa_ci_95"] == "unavailable"
    assert boot_res["critical_checks_cohens_kappa_ci_95"] == "unavailable"


def test_calibration_eligibility_multi_criterion_rule(calc):
    """Verifies that small-sample calibration uses multi-criterion rule and descriptive weighted kappa."""
    # Case 1: Meets all 5 criteria
    res_pass = calc.evaluate_calibration_eligibility(
        taxonomy_matches=9,
        critical_safety_agreement_pct=100.0,
        ordinal_mad=0.30,
        ordinal_within_one_point_pct=95.0,
        adjudicator_approved=True,
        total_taxonomy_items=10,
        descriptive_weighted_kappa=0.68,  # Below 0.75, but passed because kw is descriptive!
    )
    assert res_pass["eligible"] is True
    assert res_pass["taxonomy_exact_agreement_passed"] is True
    assert res_pass["critical_safety_agreement_passed"] is True
    assert res_pass["ordinal_mad_passed"] is True
    assert res_pass["ordinal_within_one_point_passed"] is True
    assert res_pass["adjudicator_approval_passed"] is True
    assert res_pass["descriptive_weighted_kappa"] == 0.68

    # Case 2: Fails taxonomy match (< 8/10)
    res_fail_tax = calc.evaluate_calibration_eligibility(
        taxonomy_matches=7,
        critical_safety_agreement_pct=100.0,
        ordinal_mad=0.20,
        ordinal_within_one_point_pct=100.0,
        adjudicator_approved=True,
    )
    assert res_fail_tax["eligible"] is False
    assert res_fail_tax["taxonomy_exact_agreement_passed"] is False

    # Case 3: Fails critical safety (not 100%)
    res_fail_crit = calc.evaluate_calibration_eligibility(
        taxonomy_matches=9,
        critical_safety_agreement_pct=90.0,
        ordinal_mad=0.20,
        ordinal_within_one_point_pct=100.0,
        adjudicator_approved=True,
    )
    assert res_fail_crit["eligible"] is False
    assert res_fail_crit["critical_safety_agreement_passed"] is False

    # Case 4: Fails adjudicator approval
    res_fail_adj = calc.evaluate_calibration_eligibility(
        taxonomy_matches=10,
        critical_safety_agreement_pct=100.0,
        ordinal_mad=0.10,
        ordinal_within_one_point_pct=100.0,
        adjudicator_approved=False,
    )
    assert res_fail_adj["eligible"] is False
    assert res_fail_adj["adjudicator_approval_passed"] is False


