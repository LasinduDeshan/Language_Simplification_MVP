"""Reviewer Registry Service for Stage 27.

Manages reviewer profiles, qualification validation, participation consent,
confidentiality undertakings, conflict of interest enforcement, calibration scores,
and access revocation controls.
"""

from typing import Dict, List, Optional, Any, Union
from .schemas import ReviewerProfile


class ReviewerRegistry:
    """Registry maintaining active, eligible, and revoked expert reviewers."""

    def __init__(self) -> None:
        self._reviewers: Dict[str, ReviewerProfile] = {}
        self._revocation_log: List[Dict[str, str]] = []

    def register_reviewer(
        self,
        profile: Optional[ReviewerProfile] = None,
        reviewer_id: Optional[str] = None,
        full_name: Optional[str] = None,
        qualification_track: Optional[str] = None,
        qualification_tracks: Optional[List[str]] = None,
        qualification_category: Optional[str] = None,
        experience_years: int = 5,
        consent_signed: bool = True,
        has_coi: bool = False,
        calibration_score: float = 0.85,
        account_status: str = "active",
        **kwargs: Any,
    ) -> ReviewerProfile:
        """Register a new expert reviewer profile from object or keyword arguments."""
        if profile is None:
            tracks = qualification_tracks or []
            if qualification_track and qualification_track not in tracks:
                tracks.append(qualification_track)

            profile = ReviewerProfile(
                reviewer_id=reviewer_id or f"REV-{len(self._reviewers)+1:02d}",
                professional_role=full_name or "Expert Reviewer",
                qualification_category=qualification_category or (tracks[0] if tracks else "Linguistics/Education"),
                relevant_experience_years=experience_years,
                qualification_tracks=tracks,
                conflict_of_interest_declared=has_coi,
                participation_agreement_signed=consent_signed,
                confidentiality_undertaking_signed=consent_signed,
                calibration_completed=calibration_score > 0.0,
                calibration_agreement_score=calibration_score,
                account_status=account_status,
            )

        if profile.reviewer_id in self._reviewers:
            raise ValueError(f"Reviewer with ID {profile.reviewer_id} already exists.")
        self._reviewers[profile.reviewer_id] = profile
        return profile

    def get_reviewer(self, reviewer_id: str) -> Optional[ReviewerProfile]:
        """Fetch reviewer profile by ID."""
        return self._reviewers.get(reviewer_id)

    def list_reviewers(self, active_only: bool = False) -> List[ReviewerProfile]:
        """List all registered reviewers."""
        if active_only:
            return [r for r in self._reviewers.values() if r.account_status == "active"]
        return list(self._reviewers.values())

    def get_active_reviewers(self) -> List[str]:
        """List IDs of active reviewers."""
        return [r.reviewer_id for r in self.list_reviewers(active_only=True)]

    def record_consent_and_undertaking(
        self, reviewer_id: str, participation_signed: bool, confidentiality_signed: bool
    ) -> ReviewerProfile:
        """Record participation agreement and confidentiality undertakings."""
        reviewer = self._reviewers.get(reviewer_id)
        if not reviewer:
            raise KeyError(f"Reviewer {reviewer_id} not found.")
        reviewer.participation_agreement_signed = participation_signed
        reviewer.confidentiality_undertaking_signed = confidentiality_signed
        return reviewer

    def record_calibration(
        self, reviewer_id: str, completed: bool, score: float
    ) -> ReviewerProfile:
        """Record calibration completion and agreement score."""
        reviewer = self._reviewers.get(reviewer_id)
        if not reviewer:
            raise KeyError(f"Reviewer {reviewer_id} not found.")
        reviewer.calibration_completed = completed
        reviewer.calibration_agreement_score = score
        return reviewer

    def check_dimension_authorization(self, reviewer_id: str, dimension_name: str) -> bool:
        """Verify whether reviewer has documented qualification to evaluate a specific dimension."""
        reviewer = self._reviewers.get(reviewer_id)
        if not reviewer or not reviewer.is_eligible():
            return False

        # Clinical / DLD suitability requires SLT/SLP background
        if dimension_name in ("dld_accessibility", "dld_suitability"):
            return any("Track 2" in t for t in reviewer.qualification_tracks)

        # Supervised delivery review requires Track 1, 2, or 3
        if dimension_name == "supervised_child_delivery_review":
            return any(any(k in t for t in reviewer.qualification_tracks) for k in ["Track 1", "Track 2", "Track 3"])

        # Linguistic and grammar dimensions allow Tracks 1, 4, 5
        if dimension_name in ("grammar_and_fluency", "syntactic_simplicity"):
            return any(any(k in t for t in reviewer.qualification_tracks) for k in ["Track 1", "Track 4", "Track 5"])

        # Meaning preservation allows Tracks 1, 2, 4, 5
        if dimension_name == "meaning_preservation":
            return any(any(k in t for t in reviewer.qualification_tracks) for k in ["Track 1", "Track 2", "Track 4", "Track 5"])

        # Age appropriateness allows Tracks 1, 2, 3
        if dimension_name == "age_appropriateness":
            return any(any(k in t for t in reviewer.qualification_tracks) for k in ["Track 1", "Track 2", "Track 3"])

        return True

    def is_authorized_for_dimension(self, reviewer_id: str, dimension_name: str) -> bool:
        """Alias for check_dimension_authorization."""
        return self.check_dimension_authorization(reviewer_id, dimension_name)

    def revoke_reviewer(self, reviewer_id: str, reason: str, revoked_by: str = "lead_adjudicator") -> ReviewerProfile:
        """Revoke a reviewer's access and log audit reason."""
        reviewer = self._reviewers.get(reviewer_id)
        if not reviewer:
            raise KeyError(f"Reviewer {reviewer_id} not found.")
        reviewer.account_status = "revoked"
        self._revocation_log.append({
            "reviewer_id": reviewer_id,
            "reason": reason,
            "revoked_by": revoked_by,
        })
        return reviewer

    def get_sanitized_public_registry(self) -> List[Dict[str, Any]]:
        """Return public-safe list of reviewers without PII or internal credentials."""
        return [
            {
                "reviewer_id": r.reviewer_id,
                "qualification_track": r.qualification_tracks[0] if r.qualification_tracks else r.qualification_category,
                "account_status": r.account_status,
                "calibration_passed": r.calibration_passed,
            }
            for r in self._reviewers.values()
        ]
