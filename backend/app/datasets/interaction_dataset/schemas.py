"""
V1 Pydantic schema models for private runtime interaction evidence records.
Database remains the operational source of truth; snapshots are strictly private.
"""
from datetime import datetime
from typing import List, Optional
import math
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.enums import (
    ActivityOwner, PrimaryDomain, SupportLevel, ResponseMode, Outcome
)
from app.datasets.common.metadata import GovernanceMetadata, ConsentMetadata
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION
from app.datasets.common.identifiers import is_valid_interaction_id

class PrivateInteractionRecordV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interaction_id: str = Field(..., description="Unique interaction attempt identifier")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Dataset content release version")
    
    learner_id: str = Field(..., description="Pseudonymous learner identifier (e.g. CHILD-002)")
    session_id: str = Field(..., description="Session UUID in relational database")
    activity_id: str = Field(..., description="Executed activity identifier")
    activity_owner: ActivityOwner = Field(ActivityOwner.COMPONENT_3_LANGUAGE, description="Activity owner")
    primary_domain: PrimaryDomain = Field(..., description="Educational domain updated")
    
    occurred_at: datetime = Field(default_factory=datetime.utcnow, description="Occurrence timestamp")
    attempt_number: int = Field(1, ge=1, le=3, description="Attempt number (1-3)")
    support_level_used: SupportLevel = Field(SupportLevel.MODERATE, description="Support level during attempt")
    response_mode: ResponseMode = Field(ResponseMode.MANUAL, description="Response input mode")
    
    # Private learner evidence (STRICTLY PRIVATE - EXCLUDED FROM EXPORTS)
    response_text_private: Optional[str] = Field(None, description="Raw transcription")
    normalized_response: Optional[str] = Field(None, description="Normalized response text")
    
    outcome: Outcome = Field(Outcome.IN_PROGRESS, description="Evaluation outcome")
    error_categories: List[str] = Field(default_factory=list, description="Observed educational language errors")
    response_time_ms: int = Field(0, ge=0, description="Response latency in ms")
    
    # Performance score delta
    score_before: Optional[float] = Field(None, ge=0.0, le=100.0, description="Domain score before attempt")
    score_delta: Optional[float] = Field(None, description="Score delta from attempt")
    score_after: Optional[float] = Field(None, ge=0.0, le=100.0, description="Domain score after attempt")
    evidence_count_after: int = Field(0, ge=0, description="Evidence count after attempt")
    
    adult_confirmed: bool = Field(False, description="Adult supervision confirmation")
    screening_risk_modified: bool = Field(False, description="MUST ALWAYS BE FALSE (Screening risk is read-only)")
    
    consent: ConsentMetadata = Field(default_factory=ConsentMetadata, description="Consent metadata")
    governance: GovernanceMetadata = Field(
        default_factory=lambda: GovernanceMetadata(contains_personal_data=True, is_simulated=True),
        description="Governance metadata"
    )

    @model_validator(mode="after")
    def validate_interaction_record_rules(self):
        # Invariant 1: screening_risk_modified must always be False
        if self.screening_risk_modified is not False:
            raise ValueError("screening_risk_modified must always be false (Component 1 screening risk is immutable)")
            
        # Invariant 2: interaction_id format
        if not is_valid_interaction_id(self.interaction_id):
            raise ValueError(f"Invalid interaction_id format: {self.interaction_id}")
            
        # Invariant 3: Score arithmetic consistency check (if all three scores present)
        if self.score_before is not None and self.score_delta is not None and self.score_after is not None:
            expected = self.score_before + self.score_delta
            if not math.isclose(expected, self.score_after, abs_tol=0.05):
                raise ValueError(
                    f"Score arithmetic inconsistent: score_before ({self.score_before}) + "
                    f"score_delta ({self.score_delta}) != score_after ({self.score_after})"
                )
                
        return self
