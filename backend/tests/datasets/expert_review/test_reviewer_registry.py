"""Tests for Reviewer Registry, qualification tracks, COI, and revocation."""
import pytest
from app.datasets.expert_review.reviewer_registry import ReviewerRegistry


@pytest.fixture
def registry():
    reg = ReviewerRegistry()
    reg.register_reviewer(
        reviewer_id="REV-01",
        full_name="Dr. Alice Smith",
        qualification_track="Track 2: Speech-Language Pathologist",
        experience_years=8,
        consent_signed=True,
        has_coi=False,
        calibration_score=0.92,
    )
    reg.register_reviewer(
        reviewer_id="REV-02",
        full_name="Prof. Bob Jones",
        qualification_track="Track 1: Applied Linguistics / Child Language",
        experience_years=12,
        consent_signed=True,
        has_coi=False,
        calibration_score=0.88,
    )
    return reg


def test_reviewer_authorization(registry):
    """Test authorized reviewers can evaluate appropriate dimensions."""
    # Track 2 SLT authorized for clinical/developmental dimensions
    assert registry.is_authorized_for_dimension("REV-01", "overall_suitability") is True
    assert registry.is_authorized_for_dimension("REV-01", "meaning_preservation") is True

    # Check active status
    profile = registry.get_reviewer("REV-01")
    assert profile.is_active is True
    assert profile.calibration_passed is True


def test_consent_and_coi_blocking(registry):
    """Test that reviewers without consent or with active COI are blocked."""
    registry.register_reviewer(
        reviewer_id="REV-UNCONSENTED",
        full_name="Charlie Brown",
        qualification_track="Track 4: Primary / Early Years Educator",
        experience_years=5,
        consent_signed=False,
        has_coi=False,
        calibration_score=0.85,
    )
    assert registry.is_authorized_for_dimension("REV-UNCONSENTED", "age_appropriateness") is False

    registry.register_reviewer(
        reviewer_id="REV-COI",
        full_name="Dana White",
        qualification_track="Track 1: Applied Linguistics / Child Language",
        experience_years=6,
        consent_signed=True,
        has_coi=True,
        calibration_score=0.90,
    )
    assert registry.is_authorized_for_dimension("REV-COI", "meaning_preservation") is False


def test_calibration_threshold(registry):
    """Reviewers below 0.80 calibration score fail qualification."""
    registry.register_reviewer(
        reviewer_id="REV-LOW-CALIB",
        full_name="Evan Ross",
        qualification_track="Track 3: Reading Specialist / Literacy Interventionist",
        experience_years=4,
        consent_signed=True,
        has_coi=False,
        calibration_score=0.74,  # Below 0.80
    )
    profile = registry.get_reviewer("REV-LOW-CALIB")
    assert profile.calibration_passed is False
    assert registry.is_authorized_for_dimension("REV-LOW-CALIB", "reading_ease") is False


def test_reviewer_revocation(registry):
    """Revoking reviewer access immediately disables them from active review pool."""
    assert registry.is_authorized_for_dimension("REV-01", "meaning_preservation") is True
    revoked = registry.revoke_reviewer("REV-01", reason="Conflict of interest emerged")
    assert revoked.is_active is False
    assert registry.is_authorized_for_dimension("REV-01", "meaning_preservation") is False
    assert "REV-01" not in registry.get_active_reviewers()


def test_sanitized_public_registry(registry):
    """Sanitized public export must omit names and personal details."""
    sanitized = registry.get_sanitized_public_registry()
    assert len(sanitized) >= 2
    for entry in sanitized:
        assert "full_name" not in entry
        assert "reviewer_id" in entry
        assert "qualification_track" in entry
        assert "calibration_passed" in entry
