import pytest
from app.datasets.common.metadata import GovernanceMetadata
from app.datasets.common.enums import ValidationStatus, ResearchEligibilityStatus

def test_approved_for_child_delivery_requires_approved_status():
    # Attempting approved_for_child_delivery=True on draft status must raise ValueError
    with pytest.raises(ValueError, match="approved_for_child_delivery=true requires validation_status='approved'"):
        GovernanceMetadata(
            validation_status=ValidationStatus.DRAFT,
            approved_for_child_delivery=True
        )

    # When validation_status is approved, approved_for_child_delivery is permitted
    gov = GovernanceMetadata(
        validation_status=ValidationStatus.APPROVED,
        approved_for_child_delivery=True
    )
    assert gov.approved_for_child_delivery is True

def test_research_eligible_requires_eligible_status():
    # Attempting research_eligible=True when status is not_assessed must raise ValueError
    with pytest.raises(ValueError, match="research_eligible=true requires research_eligibility_status='eligible'"):
        GovernanceMetadata(
            research_eligibility_status=ResearchEligibilityStatus.NOT_ASSESSED,
            research_eligible=True
        )

    # When status is eligible, research_eligible=True is valid
    gov = GovernanceMetadata(
        research_eligibility_status=ResearchEligibilityStatus.ELIGIBLE,
        research_eligible=True
    )
    assert gov.research_eligible is True
