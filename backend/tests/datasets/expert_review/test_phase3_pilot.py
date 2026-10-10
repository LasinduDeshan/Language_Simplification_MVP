"""Tests for Stage 27 Phase 3: Reviewer Onboarding, Calibration, and Stratified Pilot."""
import os
import pytest
from app.datasets.expert_review.pilot_runner import PilotRunner
from app.datasets.expert_review.schemas import ReviewRecordType
from app.database.db import SessionLocal


@pytest.fixture
def runner():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return PilotRunner(workspace_root=root)


def test_reviewer_onboarding_and_consent(runner):
    """Verifies that multidisciplinary reviewers across Tracks 1–5 are onboarded with consent."""
    profiles = runner.onboard_reviewers()
    assert len(profiles) == 5

    # Check tracks and eligibility
    rev1 = runner.registry.get_reviewer("REV-ENG-001")
    assert rev1 is not None
    assert "Track 2" in rev1.qualification_tracks
    assert rev1.calibration_passed is True
    assert rev1.is_eligible() is True

    rev2 = runner.registry.get_reviewer("REV-ENG-002")
    assert "Track 4" in rev2.qualification_tracks

    lead = runner.registry.get_reviewer("ADJ-LEAD-01")
    assert lead.calibration_agreement_score >= 0.90


def test_stratified_pilot_set_composition(runner):
    """Verifies the stratified pilot set covers pairs, lexicon, activities, and reformulations."""
    items = runner.build_stratified_pilot_set()
    assert len(items) == 48

    pairs = [i for i in items if i.record_type == ReviewRecordType.SIMPLIFICATION_PAIR and not i.is_reformulation_candidate]
    lexicon = [i for i in items if i.record_type == ReviewRecordType.LEXICON_ENTRY]
    activities = [i for i in items if i.record_type == ReviewRecordType.ADAPTATION_ACTIVITY]
    reformulations = [i for i in items if i.is_reformulation_candidate]

    assert len(pairs) == 20
    assert len(lexicon) == 10
    assert len(activities) == 6
    assert len(reformulations) == 12


def test_pilot_execution_and_metrics(runner):
    """Executes stratified pilot review, verifies timing metrics, agreement stats, and conflict resolution."""
    items = runner.build_stratified_pilot_set()
    results = runner.run_pilot_simulation(items)

    assert results["pilot_items_count"] == 48
    assert results["total_independent_reviews"] == 96
    assert results["average_review_time_min"] > 1.0
    assert results["disagreement_rate_pct"] > 0.0
    assert results["unresolved_adjudications"] == 0

    assert results["pilot_review_mode"] == "operational_simulation"
    assert results["human_expert_evidence"] is False
    assert results["submission_origins"]["script_generated"] == 96
    assert results["submission_origins"]["human_entered"] == 0
    assert results["submission_origins"]["llm_generated"] == 0

    stats = results["agreement_statistics"]
    assert stats["taxonomy_kappa_n"] == 48
    assert stats["critical_check_kappa_n"] == 48
    assert stats["missing_rating_count"] == 0
    assert stats["taxonomy_cohens_kappa"] >= 0.70
    assert stats["taxonomy_percent_agreement"] >= 80.0
    assert stats["icc_3_1_average_ratings"] >= 0.70
