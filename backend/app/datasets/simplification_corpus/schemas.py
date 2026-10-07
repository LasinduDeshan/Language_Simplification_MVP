"""
V1 Pydantic schema models for Simplification Corpus sentence pairs.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.enums import (
    LanguageCode, SupportLevel, DifficultyLevel, ContentType, ValidationStatus
)
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata, ReviewBlock
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION
from app.datasets.common.identifiers import is_valid_pair_id

class SimplificationPairV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pair_id: str = Field(..., description="Standardized pair identifier (e.g. SIMP-EN-000001)")
    source_activity_id: Optional[str] = Field(None, description="Optional link to parent Adaptation Test Set activity")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Dataset content release version")
    language: LanguageCode = Field(LanguageCode.EN, description="Language code")
    content_type: ContentType = Field(ContentType.INSTRUCTION, description="Content category")
    
    original_text: str = Field(..., min_length=1, description="Original source text")
    simplified_text: str = Field(..., min_length=1, description="Simplified target text")
    support_level: SupportLevel = Field(SupportLevel.MODERATE, description="Scaffolding support tier")
    age_min: int = Field(4, ge=4, le=8, description="Target minimum age in years")
    age_max: int = Field(8, ge=4, le=8, description="Target maximum age in years")
    
    original_difficulty: Optional[DifficultyLevel] = Field(DifficultyLevel.MEDIUM, description="Original complexity")
    simplified_difficulty: Optional[DifficultyLevel] = Field(DifficultyLevel.EASY, description="Simplified complexity")
    operations: List[str] = Field(default_factory=list, description="Linguistic simplification operations applied")
    protected_meaning_units: List[str] = Field(default_factory=list, description="Preserved meaning tokens")
    
    review: ReviewBlock = Field(default_factory=ReviewBlock, description="Human review and evaluation scores")
    source: SourceMetadata = Field(default_factory=SourceMetadata, description="Lineage metadata")
    rights: RightsMetadata = Field(default_factory=RightsMetadata, description="Rights metadata")
    governance: GovernanceMetadata = Field(default_factory=GovernanceMetadata, description="Governance metadata")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")

    @model_validator(mode="after")
    def validate_simplification_pair_rules(self):
        # Age validation
        if self.age_min > self.age_max:
            raise ValueError(f"age_min ({self.age_min}) cannot exceed age_max ({self.age_max})")
            
        # Pair ID validation
        if not is_valid_pair_id(self.pair_id):
            raise ValueError(f"Invalid pair_id format: {self.pair_id}")
            
        # Approved status requires reviewer evidence
        if self.governance.validation_status == ValidationStatus.APPROVED:
            if not self.review.is_complete_approval():
                raise ValueError("validation_status='approved' requires reviewer_id, reviewer_role, and reviewed_at in review block")
                
        return self
