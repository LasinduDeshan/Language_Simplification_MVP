from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Component1ScreeningInputSchema(BaseModel):
    """
    Contract schema for screening profiles received from Component 1.
    Component 1 is the sole owner of the DLD risk indicator.
    """
    schema_version: str = Field("1.0", description="Contract schema version")
    learner_id: str = Field(..., description="Pseudonymous learner identifier e.g. CHILD-002")
    age: Optional[int] = Field(None, ge=4, le=8)
    preferred_language: str = Field("en")
    risk_level: str = Field(..., pattern="^(low|moderate|high)$", description="Read-only clinical screening risk from Component 1")
    vocabulary_score: float = Field(50.0, ge=0.0, le=100.0)
    grammar_score: float = Field(50.0, ge=0.0, le=100.0)
    comprehension_score: float = Field(50.0, ge=0.0, le=100.0)
    instruction_following_score: float = Field(50.0, ge=0.0, le=100.0)
    screening_version: str = Field("mock-c1-1.0", description="Screening protocol/battery version")
    source: str = Field("component_1", description="Source component identifier")
    assessed_at: Optional[datetime] = None
    validation_reference: Optional[str] = None
    event_id: Optional[str] = Field(None, description="Unique event identifier for idempotency tracking")
    authorized_role: Optional[str] = Field("component_1_screening", description="Authorized service role")
    
    # Simulation & research guardrails
    is_simulated: bool = Field(True, description="True for simulated development fixtures")
    environment: str = Field("development", description="Environment identifier")
    research_eligible: bool = Field(False, description="Simulated records must never enter real research datasets")

    model_config = ConfigDict(extra="ignore")
