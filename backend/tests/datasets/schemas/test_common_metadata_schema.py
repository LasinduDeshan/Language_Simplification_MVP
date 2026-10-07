import pytest
from datetime import datetime
from app.datasets.common.metadata import (
    SourceMetadata, RightsMetadata, GovernanceMetadata, ReviewBlock, ConsentMetadata
)
from app.datasets.common.enums import (
    SourceType, ValidationStatus, ResearchEligibilityStatus, ConsentStatus
)

def test_source_metadata_defaults():
    src = SourceMetadata(source_name="Test Source")
    assert src.source_type == SourceType.TEAM_AUTHORED
    assert src.created_by_role == "project_team"
    assert isinstance(src.created_at, datetime)

def test_rights_metadata_restrictive_defaults():
    rights = RightsMetadata()
    assert rights.licence_id == "project-internal"
    assert rights.redistribution_allowed is False
    assert rights.commercial_use_allowed is False
    assert rights.external_api_processing_allowed is False

def test_governance_metadata_restrictive_defaults():
    gov = GovernanceMetadata()
    assert gov.validation_status == ValidationStatus.DRAFT
    assert gov.research_eligibility_status == ResearchEligibilityStatus.NOT_ASSESSED
    assert gov.research_eligible is False
    assert gov.approved_for_child_delivery is False

def test_review_block_approval_check():
    rb = ReviewBlock()
    assert not rb.is_complete_approval()
    
    rb_complete = ReviewBlock(
        reviewer_id="REV-001",
        reviewer_role="linguist",
        reviewed_at=datetime.utcnow()
    )
    assert rb_complete.is_complete_approval()

def test_extra_fields_forbidden():
    with pytest.raises(Exception):
        SourceMetadata(source_name="Test", unexpected_field="invalid")
