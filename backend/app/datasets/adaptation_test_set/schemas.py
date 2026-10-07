"""
V1 Pydantic schema models for Adaptation Test Set activities.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.enums import (
    LanguageCode, ActivityOwner, PrimaryDomain, DifficultyLevel, AdaptationPolicy
)
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION
from app.datasets.common.identifiers import is_valid_activity_id

class ProtectedElements(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: Optional[str] = Field(None, description="Protected answer key (MUST NEVER LEAK TO CHILD)")
    elements: List[str] = Field(default_factory=list, description="Protected words or structural elements")
    target_skill_locked: bool = Field(True, description="Whether target skill cannot be altered")
    acceptable_answers: List[str] = Field(default_factory=list, description="Alternative acceptable responses")

class AdaptationRecordV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity_id: str = Field(..., description="Standardized activity identifier (e.g. C3-EN-VOC-0001)")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Dataset content release version")
    activity_owner: ActivityOwner = Field(ActivityOwner.COMPONENT_3_LANGUAGE, description="Owning component")
    language: LanguageCode = Field(LanguageCode.EN, description="Language code")
    activity_type: str = Field("standard", description="Type of task (naming/word_order/cloze/action)")
    primary_domain: PrimaryDomain = Field(..., description="Primary educational domain")
    target_skill: Optional[str] = Field(None, description="Fine-grained pedagogical target skill")
    age_min: int = Field(4, ge=4, le=8, description="Target minimum age in years")
    age_max: int = Field(8, ge=4, le=8, description="Target maximum age in years")
    difficulty: DifficultyLevel = Field(DifficultyLevel.MEDIUM, description="Baseline difficulty")
    
    original_instruction: str = Field(..., min_length=1, description="Original unsimplified instruction")
    child_friendly_instruction: Optional[str] = Field(None, description="Pre-simplified variant")
    stimulus: Optional[Any] = Field(None, description="Visual or textual stimulus payload")
    options: Optional[List[str]] = Field(None, description="Multiple choice options")
    passage: Optional[str] = Field(None, description="Reading or listening passage")
    
    protected: ProtectedElements = Field(default_factory=ProtectedElements, description="Protected elements and answer keys")
    adaptation_policy: AdaptationPolicy = Field(AdaptationPolicy.INSTRUCTION_ONLY, description="Governed adaptation policy")
    allowed_transformations: List[str] = Field(default_factory=lambda: ["simplify_instruction", "add_audio", "present_visual_cues"])
    forbidden_transformations: List[str] = Field(default_factory=lambda: ["change_stimulus", "expose_answer", "change_target_skill"])
    
    source: SourceMetadata = Field(default_factory=SourceMetadata, description="Lineage metadata")
    rights: RightsMetadata = Field(default_factory=RightsMetadata, description="Rights metadata")
    governance: GovernanceMetadata = Field(default_factory=GovernanceMetadata, description="Governance metadata")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Record update timestamp")

    @model_validator(mode="after")
    def validate_adaptation_record_rules(self):
        # Age validation
        if self.age_min > self.age_max:
            raise ValueError(f"age_min ({self.age_min}) cannot exceed age_max ({self.age_max})")
            
        # Activity ID format validation (permitting Stage 13 legacy IDs)
        if not is_valid_activity_id(self.activity_id):
            raise ValueError(f"Invalid activity_id format: {self.activity_id}")
            
        return self

class ChildSafeActivityView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity_id: str
    language: str
    activity_type: str
    primary_domain: str
    age_min: int
    age_max: int
    difficulty: str
    original_instruction: str
    child_friendly_instruction: Optional[str] = None
    stimulus: Optional[Any] = None
    options: Optional[List[str]] = None
    passage: Optional[str] = None
    adaptation_policy: str
    allowed_transformations: List[str]
