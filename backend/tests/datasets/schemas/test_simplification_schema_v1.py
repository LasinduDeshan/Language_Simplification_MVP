import pytest
from datetime import datetime
from app.datasets.simplification_corpus.schemas import SimplificationPairV1
from app.datasets.common.enums import (
    LanguageCode, SupportLevel, ContentType, ValidationStatus
)
from app.datasets.common.metadata import GovernanceMetadata, ReviewBlock

def test_valid_simplification_pair():
    pair = SimplificationPairV1(
        pair_id="SIMP-EN-000001",
        language=LanguageCode.EN,
        content_type=ContentType.INSTRUCTION,
        original_text="Before choosing the red object, place the small cup beside the box.",
        simplified_text="Put the small cup next to the box. Then choose the red object.",
        support_level=SupportLevel.STRONG,
        age_min=4,
        age_max=8,
        operations=["sentence_splitting", "lexical_substitution"]
    )
    assert pair.pair_id == "SIMP-EN-000001"
    assert pair.governance.validation_status == ValidationStatus.DRAFT
    assert pair.governance.research_eligible is False
    assert pair.governance.approved_for_child_delivery is False

def test_approval_requires_reviewer_evidence():
    # Setting validation_status=approved with empty review block must raise ValueError
    with pytest.raises(ValueError, match="validation_status='approved' requires reviewer_id"):
        SimplificationPairV1(
            pair_id="SIMP-EN-000002",
            original_text="Original",
            simplified_text="Simplified",
            governance=GovernanceMetadata(validation_status=ValidationStatus.APPROVED),
            review=ReviewBlock()
        )

    # Valid with full review block
    valid_pair = SimplificationPairV1(
        pair_id="SIMP-EN-000002",
        original_text="Original",
        simplified_text="Simplified",
        governance=GovernanceMetadata(validation_status=ValidationStatus.APPROVED),
        review=ReviewBlock(
            reviewer_id="REV-001",
            reviewer_role="linguist",
            reviewed_at=datetime.utcnow()
        )
    )
    assert valid_pair.governance.validation_status == ValidationStatus.APPROVED
