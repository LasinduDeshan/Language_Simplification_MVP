"""
Stage 34 — Reviewer Eligibility and Registry Service
Enforces reviewer qualification criteria, competency boundaries, conflict declarations,
and minimum panel composition (at least 6 unique qualified individuals).
"""

from typing import Any, Dict, List, Optional
from .enums import ExperienceBand, ReviewerRole, TrainingStatus
from .schemas import CompetencyDeclarations, ReviewerEligibility


class ReviewerRegistry:
    def __init__(self):
        self._reviewers: Dict[str, ReviewerEligibility] = {}

    def register_reviewer(self, reviewer: ReviewerEligibility) -> ReviewerEligibility:
        if reviewer.reviewer_id in self._reviewers:
            raise ValueError(f"Reviewer {reviewer.reviewer_id} already registered.")

        # Require complete conflict declaration and consent
        if not reviewer.conflict_declaration_completed:
            raise ValueError(f"Reviewer {reviewer.reviewer_id} has incomplete conflict declaration.")
        if not reviewer.consent_version_hash:
            raise ValueError(f"Reviewer {reviewer.reviewer_id} lacks consent version hash.")

        self._reviewers[reviewer.reviewer_id] = reviewer
        return reviewer

    def get_reviewer(self, reviewer_id: str) -> Optional[ReviewerEligibility]:
        return self._reviewers.get(reviewer_id)

    def list_reviewers(self, qualified_only: bool = True) -> List[ReviewerEligibility]:
        if qualified_only:
            return [r for r in self._reviewers.values() if r.training_status == TrainingStatus.QUALIFIED]
        return list(self._reviewers.values())

    def verify_panel_composition(self) -> Dict[str, Any]:
        """Verifies that the qualified panel contains at least 6 unique individuals satisfying role quotas."""
        qualified = [r for r in self._reviewers.values() if r.training_status == TrainingStatus.QUALIFIED]

        unique_count = len(qualified)
        linguists = [r for r in qualified if ReviewerRole.SINHALA_LINGUIST in r.roles]
        educators = [r for r in qualified if ReviewerRole.EARLY_CHILDHOOD_EDUCATOR in r.roles]
        child_devs = [r for r in qualified if ReviewerRole.CHILD_DEVELOPMENT_SPECIALIST in r.roles]
        adjudicators = [r for r in qualified if ReviewerRole.INDEPENDENT_ADJUDICATOR in r.roles]

        # Check quotas
        is_valid = (
            unique_count >= 6
            and len(linguists) >= 2
            and len(educators) >= 2
            and len(child_devs) >= 1
            and len(adjudicators) >= 1
        )

        return {
            "is_valid": is_valid,
            "unique_qualified_count": unique_count,
            "linguists_count": len(linguists),
            "educators_count": len(educators),
            "child_dev_count": len(child_devs),
            "adjudicator_count": len(adjudicators),
            "linguist_ids": [r.reviewer_id for r in linguists],
            "educator_ids": [r.reviewer_id for r in educators],
            "child_dev_ids": [r.reviewer_id for r in child_devs],
            "adjudicator_ids": [r.reviewer_id for r in adjudicators],
        }

    def to_sanitized_records(self) -> List[Dict[str, Any]]:
        """Returns public git-safe dictionary list containing no PII, contact info, or signatures."""
        sanitized = []
        for r in self._reviewers.values():
            sanitized.append({
                "reviewer_id": r.reviewer_id,
                "roles": [role.value for role in r.roles],
                "years_experience_band": r.years_relevant_experience_band.value,
                "native_or_professional_sinhala": r.native_or_professional_sinhala_proficiency,
                "ages_4_to_8_experience": r.ages_4_to_8_experience,
                "competency_declarations": r.competency_declarations.model_dump(),
                "training_status": r.training_status.value,
                "is_project_team_member": r.is_project_team_member,
            })
        return sanitized
