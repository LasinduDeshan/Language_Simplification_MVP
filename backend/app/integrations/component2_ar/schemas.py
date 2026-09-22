from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

class Component2AROutputSchema(BaseModel):
    """
    AR payload contract schema for Component 2 (Unity / AR Environment).
    """
    schema_version: str = Field("1.0", description="Contract schema version")
    task_id: str = Field(..., description="Task code e.g. TASK-VOCAB-001")
    language: str = Field("en", description="Target language code")
    instruction: str = Field(..., description="Validated child-friendly instruction")
    support_level: str = Field("moderate", pattern="^(mild|moderate|strong)$")
    steps: List[str] = Field(default_factory=list, description="Sequential action steps for AR presentation")
    vocabulary_support: List[Dict[str, str]] = Field(default_factory=list, description="Key target words with child definitions/icons")
    audio_text: str = Field(..., description="Verbatim text for speech synthesis")
    validation_status: str = Field("approved", description="Pedagogical validation status")
    delivery_status: str = Field("not_connected", description="Integration delivery status: not_connected | mock | sent")
    
    # Simulation & research guardrails
    is_simulated: bool = Field(True, description="True for local development preview payloads")
    environment: str = Field("development", description="Environment identifier")
    research_eligible: bool = Field(False, description="Simulated records must never enter real research datasets")

    model_config = ConfigDict(extra="ignore")
