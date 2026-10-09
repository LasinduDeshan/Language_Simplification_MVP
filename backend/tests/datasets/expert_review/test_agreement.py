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
