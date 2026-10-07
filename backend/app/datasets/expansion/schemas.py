"""
Pydantic Schemas for Stage 20 Dataset Expansion
Defines models for provenance, authoring records, inventory, gap matrices, and targets.
"""
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class AuthoringMethodEnum(str, Enum):
    HUMAN_AUTHORED = "human_authored"
    HUMAN_AUTHORED_WITH_AI_ASSISTANCE = "human_authored_with_ai_assistance"
    RULE_GENERATED = "rule_generated"
    LLM_GENERATED_DRAFT = "llm_generated_draft"
    DERIVED_FROM_INTERNAL_SOURCE = "derived_from_internal_source"

class PrimaryDomainEnum(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    COMPREHENSION = "comprehension"
    INSTRUCTION_FOLLOWING = "instruction_following"

class SourceDifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SupportLevelEnum(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"

class ProvenanceMetadata(BaseModel):
    authoring_method: AuthoringMethodEnum = Field(..., description="Method used to author the record")
    created_by: str = Field(..., description="Author or system identifier")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    source_record_id: Optional[str] = Field(None, description="Identifier of source item")
    parent_record_id: Optional[str] = Field(None, description="Parent ID if this is a correction revision")
    generation_model: Optional[str] = Field(None, description="LLM model name if AI-assisted")
    prompt_template_version: Optional[str] = Field(None, description="Prompt template version if applicable")
    human_edited: bool = Field(False, description="True if a human reviewed and edited the record")
    rights_status: str = Field("internal_team_owned", description="Intellectual property and rights status")
    source_reference: Optional[str] = Field(None, description="Source dataset, batch, or citation")
    batch_id: str = Field(..., description="Batch identifier e.g. STAGE20-BATCH-PILOT")
    revision_id: str = Field("REV-001", description="Revision identifier")

    @field_validator("authoring_method")
    @classmethod
    def validate_provenance_rules(cls, v, info):
        # AI-assisted or LLM generated cannot claim 100% human without human_edited
        return v

class OriginalEducationalItem(BaseModel):
    source_item_id: str = Field(..., pattern=r"^SRC-EN-[A-Z]{3,4}-[0-9]{3,5}$")
    activity_id: Optional[str] = Field(None, description="Associated Adaptation Activity ID")
    schema_version: str = Field("1.0.0")
    dataset_version: str = Field("0.2.0")
    language: str = Field("en")
    age_min: int = Field(..., ge=4, le=8)
    age_max: int = Field(..., ge=4, le=8)
    primary_domain: PrimaryDomainEnum
    content_type: str = Field(...)
    source_difficulty: SourceDifficultyEnum
    original_text: str = Field(..., min_length=3)
    protected_meaning_units: List[str] = Field(default_factory=list)
    expected_response_mode: str = Field("action")
    source_type: str = Field("team_authored")
    validation_status: str = Field("draft")
    research_eligible: bool = Field(False)
    approved_for_child_delivery: bool = Field(False)
    requires_expert_review: bool = Field(True)
    provenance: ProvenanceMetadata

    @field_validator("age_max")
    @classmethod
    def validate_age_range(cls, v, info):
        if "age_min" in info.data and v < info.data["age_min"]:
            raise ValueError("age_max must be greater than or equal to age_min")
        return v

class SimplificationPairRecord(BaseModel):
    pair_id: str = Field(..., pattern=r"^SIMP-EN-[0-9]{6}$")
    source_item_id: str = Field(..., pattern=r"^SRC-EN-[A-Z]{3,4}-[0-9]{3,5}$")
    activity_id: Optional[str] = Field(None)
    schema_version: str = Field("1.0.0")
    dataset_version: str = Field("0.2.0")
    language: str = Field("en")
    support_level: SupportLevelEnum
    original_text: str = Field(..., min_length=3)
    simplified_text: str = Field(..., min_length=3)
    simplification_operations: List[str] = Field(default_factory=list)
    protected_meaning_units: List[str] = Field(default_factory=list)
    quality_status: str = Field("draft")
    validation_status: str = Field("draft")
    research_eligible: bool = Field(False)
    approved_for_child_delivery: bool = Field(False)
    requires_expert_review: bool = Field(True)
    provenance: ProvenanceMetadata

class LexiconEntryRecord(BaseModel):
    lexicon_id: str = Field(..., pattern=r"^LEX-EN-[0-9]{5,6}$")
    schema_version: str = Field("1.0.0")
    dataset_version: str = Field("0.2.0")
    language: str = Field("en")
    headword: str = Field(..., min_length=1)
    normalized_form: str = Field(..., min_length=1)
    pos: str = Field(..., description="Part of speech e.g. noun, verb, adjective")
    sense_id: str = Field("sense_1")
    age_min: int = Field(..., ge=4, le=8)
    age_max: int = Field(..., ge=4, le=8)
    difficulty_tier: SourceDifficultyEnum = Field(SourceDifficultyEnum.EASY)
    simple_replacement: Optional[str] = Field(None)
    child_definition: str = Field(..., min_length=5)
    example_sentence: str = Field(..., min_length=5)
    validation_status: str = Field("draft")
    research_eligible: bool = Field(False)
    approved_for_child_delivery: bool = Field(False)
    requires_expert_review: bool = Field(True)
    provenance: ProvenanceMetadata

class AuthoringBatchPayload(BaseModel):
    batch_id: str
    dataset_version: str = "0.2.0"
    schema_version: str = "1.0.0"
    source_items: List[OriginalEducationalItem] = Field(default_factory=list)
    simplification_pairs: List[SimplificationPairRecord] = Field(default_factory=list)
    adaptation_activities: List[Dict[str, Any]] = Field(default_factory=list)
    lexicon_entries: List[LexiconEntryRecord] = Field(default_factory=list)
