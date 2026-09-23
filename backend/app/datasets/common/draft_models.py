from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

SCHEMA_STATUS_DRAFT = "draft_stage13"

class MigrationDisposition(str, Enum):
    MIGRATED = "migrated"
    EXCLUDED = "excluded"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class MigrationMappingRecord(BaseModel):
    """
    Tracks bidirectional source-to-target ID and path mapping for auditability.
    """
    schema_status: str = SCHEMA_STATUS_DRAFT
    source_path: str = Field(..., description="Original file path or database table")
    source_id: str = Field(..., description="Original identifier (e.g. task_code, session_id)")
    target_layer: str = Field(..., description="Destination dataset layer")
    target_id: str = Field(..., description="Standardized target identifier (e.g. C3-EN-VOC-0001)")
    disposition: MigrationDisposition = Field(MigrationDisposition.MIGRATED)
    migration_timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    model_config = ConfigDict(extra="ignore")

class DraftAdaptationRecord(BaseModel):
    """
    Draft Stage 13 data transfer object for Adaptation Test Set activities.
    """
    schema_status: str = SCHEMA_STATUS_DRAFT
    activity_id: str = Field(..., description="Standardized activity ID e.g. C3-EN-GRAM-0001")
    legacy_task_code: Optional[str] = None
    activity_owner: str = Field("component_3", pattern="^(component_1|component_2_ar|component_3)$")
    language: str = Field("en")
    primary_domain: str = Field(..., pattern="^(vocabulary|grammar|comprehension|sentence_and_instruction|instruction_following)$")
    activity_type: str = Field("standard")
    target_skill: Optional[str] = None
    age_min: int = Field(4, ge=4)
    age_max: int = Field(8, le=8)
    base_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    
    # Instructions and stimuli
    original_instruction: str
    child_friendly_instruction: Optional[str] = None
    stimulus: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    passage: Optional[str] = None
    
    # Answers and Protection boundaries
    protected_answer: Optional[str] = Field(None, description="Must NEVER leak into child-facing views")
    protected_elements: List[str] = Field(default_factory=list)
    acceptable_answers: List[str] = Field(default_factory=list)
    expected_concepts: List[str] = Field(default_factory=list)
    
    # Adaptation Governance
    adaptation_policy: str = Field("instruction_only", pattern="^(none|presentation_only|instruction_only|controlled)$")
    allowed_transformations: List[str] = Field(default_factory=lambda: ["simplify_instruction", "add_audio", "present_visual_cues"])
    forbidden_transformations: List[str] = Field(default_factory=lambda: ["change_stimulus", "expose_answer", "change_target_skill"])
    support_versions: Optional[Dict[str, str]] = None
    
    # Simulation & research flags
    is_simulated: bool = Field(True)
    research_eligible: bool = Field(False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(extra="ignore")

class DraftSimplificationPair(BaseModel):
    """
    Draft Stage 13 data transfer object for Simplification Corpus sentence pairs.
    """
    schema_status: str = SCHEMA_STATUS_DRAFT
    pair_id: str = Field(..., description="Standardized pair ID e.g. SIMP-EN-0001")
    source_activity_id: Optional[str] = None
    language: str = Field("en")
    content_type: str = Field("instruction", pattern="^(instruction|stimulus_prompt|feedback_cue|vocabulary_definition)$")
    original_text: str
    simplified_text: str
    support_level: str = Field("moderate", pattern="^(mild|moderate|strong)$")
    age_min: int = Field(4, ge=4)
    age_max: int = Field(8, le=8)
    operations: List[str] = Field(default_factory=list, description="e.g. lexical_substitution, sentence_splitting, visual_scaffolding")
    protected_meaning_units: List[str] = Field(default_factory=list)
    source_type: str = Field("team_authored", pattern="^(team_authored|adaptation_engine_generated|expert_curated)$")
    validation_status: str = Field("draft", pattern="^(draft|in_review|approved)$")
    research_eligible: bool = Field(False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(extra="ignore")

class DraftInteractionRecord(BaseModel):
    """
    Draft Stage 13 data transfer object for Private Interaction Dataset snapshots.
    """
    schema_status: str = SCHEMA_STATUS_DRAFT
    interaction_id: str = Field(..., description="Unique interaction ID e.g. INT-20260923-000001")
    session_id: str
    learner_id: str = Field(..., description="Pseudonymous learner identifier")
    activity_id: str
    activity_owner: str = Field("component_3")
    attempt_number: int = Field(1, ge=1, le=3)
    support_level_used: str = Field("moderate", pattern="^(mild|moderate|strong)$")
    response_mode: str = Field("manual_transcript")
    
    # Private learner transcripts (STRICTLY PRIVATE)
    response_text_private: Optional[str] = Field(None, description="Raw transcription - private storage only")
    normalized_response: Optional[str] = None
    outcome: str = Field("in_progress")
    error_categories: List[str] = Field(default_factory=list)
    response_time_ms: int = Field(0, ge=0)
    
    # Educational Scoring snapshot (Immutable screening risk)
    updated_domain: str = Field("vocabulary", pattern="^(vocabulary|grammar|comprehension|sentence_and_instruction|instruction_following)$")
    score_before: Optional[float] = None
    score_delta: Optional[float] = None
    score_after: Optional[float] = None
    evidence_count_after: int = Field(0, ge=0)
    
    adult_confirmed: bool = Field(False)
    screening_risk_modified: bool = Field(False, description="Strictly false: interaction outcomes never mutate screening risk")
    consent_status: str = Field("not_verified", pattern="^(verified|not_verified|revoked)$")
    is_simulated: bool = Field(True)
    research_eligible: bool = Field(False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(extra="ignore")
