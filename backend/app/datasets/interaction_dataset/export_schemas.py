"""
V1 Pydantic schema for de-identified interaction exports.
Uses an explicit allowlist to prevent raw transcript or notes leakage.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.datasets.common.enums import (
    PrimaryDomain, SupportLevel, ResponseMode, Outcome
)
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION

class DeidentifiedInteractionExportV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    interaction_id: str = Field(..., description="De-identified interaction ID")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Dataset version")
    
    learner_id: str = Field(..., description="Pseudonymous learner identifier")
    activity_id: str = Field(..., description="Activity identifier")
    primary_domain: PrimaryDomain = Field(..., description="Primary domain")
    occurred_at: datetime = Field(..., description="Occurrence timestamp")
    attempt_number: int = Field(..., ge=1, le=3, description="Attempt sequence number")
    support_level_used: SupportLevel = Field(..., description="Support tier used")
    response_mode: ResponseMode = Field(..., description="Response input channel")
    
    outcome: Outcome = Field(..., description="Outcome evaluation")
    error_categories: List[str] = Field(default_factory=list, description="Observed language error categories")
    response_time_ms: int = Field(..., ge=0, description="Response latency in ms")
    score_delta: Optional[float] = Field(None, description="Score delta")
    local_preliminary_trend: Optional[str] = Field(None, description="Local preliminary trend indicator for Component 4")
