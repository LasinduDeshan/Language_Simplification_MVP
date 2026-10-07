from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class DomainPerformancePayload(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Educational performance score in this domain")
    previous_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    score_delta: Optional[float] = None
    evidence_count: int = Field(..., ge=0, description="Number of confirmed learning activities completed in this domain")
    local_preliminary_trend: str = Field("stable", description="Preliminary local trend (Component 4 produces official longitudinal analytics)")
    recent_activity_scores: List[float] = Field(default_factory=list)
    latest_updated_at: Optional[datetime] = None

class Component4PerformanceExportSchema(BaseModel):
    """
    Export contract for Component 4 (Learning Analytics & Longitudinal Progression).
    """
    schema_version: str = Field("1.0", description="Contract schema version")
    learner_id: str = Field(..., description="Pseudonymous learner identifier e.g. CHILD-002")
    screening_risk_level: str = Field(..., description="Read-only screening risk level imported from Component 1")
    screening_source: str = Field("component_1", description="Source component for screening risk")
    risk_modified_by_component_3: bool = Field(False, description="Strictly false: language simplification component never alters screening risk")
    recommended_support_level: str = Field("moderate", pattern="^(mild|moderate|strong)$")
    
    # 4 Educational Performance Domains
    performance_profile: Dict[str, DomainPerformancePayload] = Field(
        ...,
        description="Performance data for vocabulary, grammar, comprehension, and instruction_following"
    )
    
    # Latest Activity Snapshot
    latest_session_id: Optional[str] = None
    latest_task_code: Optional[str] = None
    latest_outcome: Optional[str] = None
    latest_independent_success: Optional[bool] = None
    latest_attempt_count: Optional[int] = None
    
    # Simulation & research guardrails
    is_simulated: bool = Field(True, description="True for simulated development previews")
    environment: str = Field("development", description="Environment identifier")
    research_eligible: bool = Field(False, description="Simulated records must never enter real research datasets")
    export_timestamp: datetime = Field(default_factory=datetime.utcnow)
    export_status: str = Field("generated_locally_not_delivered", description="Integration status indicator")

    model_config = ConfigDict(extra="ignore")
