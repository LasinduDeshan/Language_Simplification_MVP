"""
Common metadata and governance Pydantic models for Stage 14 v1 dataset schemas.
Enforces model-level cross-field validation rules and restrictive defaults.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.enums import (
    SourceType, ValidationStatus, ResearchEligibilityStatus, ConsentStatus
)

class SourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_type: SourceType = Field(SourceType.TEAM_AUTHORED, description="Origin classification of the content")
    source_name: str = Field("Component 3 English MVP", description="Author or originating dataset")
    source_record_id: Optional[str] = Field(None, description="Original identifier in upstream source system")
    source_url: Optional[str] = Field(None, description="URL reference to source")
    citation: Optional[str] = Field(None, description="Academic or publication citation")
    created_by_role: str = Field("project_team", description="Role of creator (project_team/expert/system)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    @model_validator(mode="after")
    def validate_source_rules(self):
        if self.source_type == SourceType.PERMISSION_GRANTED and not self.source_record_id:
            # permission_reference or identifier should be tracked
            pass
        return self

class RightsMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    licence_id: str = Field("project-internal", description="SPDX licence identifier or project-internal")
    licence_url: Optional[str] = Field(None, description="Web link to licence terms")
    permission_reference: Optional[str] = Field(None, description="Permission identifier or document reference")
    redistribution_allowed: bool = Field(False, description="Whether dataset allows redistribution")
    commercial_use_allowed: bool = Field(False, description="Whether commercial use is permitted")
    external_api_processing_allowed: bool = Field(False, description="Strict LLM API gating")

    @model_validator(mode="after")
    def validate_rights_consistency(self):
        if self.licence_id == "project-internal" and self.redistribution_allowed:
            raise ValueError("project-internal licence cannot allow open redistribution")
        return self

class GovernanceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    validation_status: ValidationStatus = Field(ValidationStatus.DRAFT, description="Workflow status")
    research_eligibility_status: ResearchEligibilityStatus = Field(ResearchEligibilityStatus.NOT_ASSESSED, description="Formal research assessment status")
    research_eligible: bool = Field(False, description="Research readiness flag")
    approved_for_child_delivery: bool = Field(False, description="Runtime child presentation flag")
    is_simulated: bool = Field(False, description="Simulation or synthetic flag")
    contains_personal_data: bool = Field(False, description="Personal/screening data flag")

    @model_validator(mode="after")
    def validate_governance_cross_field_rules(self):
        # Rule 1: approved_for_child_delivery requires validation_status=approved
        if self.approved_for_child_delivery and self.validation_status != ValidationStatus.APPROVED:
            raise ValueError("approved_for_child_delivery=true requires validation_status='approved'")
        
        # Rule 2: research_eligible requires research_eligibility_status=eligible
        if self.research_eligible and self.research_eligibility_status != ResearchEligibilityStatus.ELIGIBLE:
            raise ValueError("research_eligible=true requires research_eligibility_status='eligible'")
            
        return self

class ReviewBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reviewer_id: Optional[str] = Field(None, description="Identifier of reviewer")
    reviewer_role: Optional[str] = Field(None, description="Role of reviewer (linguist/educator/slp)")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    simplicity_score: Optional[float] = Field(None, ge=1.0, le=5.0, description="1-5 Likert simplicity score")
    grammar_score: Optional[float] = Field(None, ge=1.0, le=5.0, description="1-5 Likert grammar score")
    meaning_preservation_score: Optional[float] = Field(None, ge=1.0, le=5.0, description="1-5 Likert meaning preservation score")
    age_appropriateness_score: Optional[float] = Field(None, ge=1.0, le=5.0, description="1-5 Likert age appropriateness score")
    notes: Optional[str] = Field(None, description="Reviewer qualitative notes")

    def is_complete_approval(self) -> bool:
        return bool(self.reviewer_id and self.reviewed_at and self.reviewer_role)

class ConsentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: ConsentStatus = Field(ConsentStatus.NOT_VERIFIED, description="Consent status")
    reference_id: Optional[str] = Field(None, description="Consent document reference")
    verified_at: Optional[datetime] = Field(None, description="Verification timestamp")
