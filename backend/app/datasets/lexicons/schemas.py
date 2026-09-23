"""
V1 Pydantic schema models for Lexicon Repository entries.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.enums import LanguageCode
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION
from app.datasets.common.identifiers import is_valid_lexicon_id

class LexiconEntryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry_id: str = Field(..., description="Unique lexicon entry identifier (e.g. LEX-EN-000001)")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Dataset content release version")
    language: LanguageCode = Field(LanguageCode.EN, description="Language code")
    
    word: str = Field(..., min_length=1, description="Target headword or complex lemma")
    normalized_form: str = Field(..., min_length=1, description="Lowercased stripped normalized word")
    part_of_speech: Optional[str] = Field(None, description="Part of speech (noun/verb/adjective/preposition)")
    age_band: Optional[str] = Field(None, description="Target developmental age band (e.g. 4-6, 6-8)")
    difficulty_tier: int = Field(2, ge=1, le=3, description="Tier (1=basic, 2=academic/high-freq, 3=domain specific)")
    
    simpler_alternatives: List[str] = Field(default_factory=list, description="Child-friendly substitution candidates")
    child_friendly_definition: Optional[str] = Field(None, description="Simple child-friendly explanation")
    example_sentence: Optional[str] = Field(None, description="Illustrative example sentence")
    
    source: SourceMetadata = Field(default_factory=SourceMetadata, description="Lineage metadata")
    rights: RightsMetadata = Field(default_factory=RightsMetadata, description="Rights metadata")
    governance: GovernanceMetadata = Field(default_factory=GovernanceMetadata, description="Governance metadata")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")

    @model_validator(mode="after")
    def validate_lexicon_entry_rules(self):
        if not is_valid_lexicon_id(self.entry_id):
            raise ValueError(f"Invalid entry_id format: {self.entry_id}")
        return self
