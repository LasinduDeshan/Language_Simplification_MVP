"""
Release manifest Pydantic models for Stage 14 release integrity and accounting.
"""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.datasets.common.versions import CURRENT_SCHEMA_VERSION, CURRENT_DATASET_VERSION

class RecordCountSummaryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    adaptation_activities: int = Field(..., ge=0, description="Total activities in Adaptation Test Set")
    simplification_pairs: int = Field(..., ge=0, description="Total pairs in Simplification Corpus")
    lexicon_entries: int = Field(..., ge=0, description="Total entries in Lexicon Repository")
    total_reusable_records: int = Field(..., ge=0, description="Sum of reusable records across layers")

class ReleaseFileEntryV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str = Field(..., description="Relative file path within repository")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    sha256: str = Field(..., min_length=64, max_length=64, description="Complete 64-character SHA-256 hash")
    record_count: Optional[int] = Field(None, ge=0, description="Record count inside file")

class ReleaseManifestV1(BaseModel):
    model_config = ConfigDict(extra="forbid")
    manifest_id: str = Field(..., description="Unique manifest ID (e.g. MANIFEST-0.1.0)")
    dataset_name: str = Field("Language_Simplification_MVP_Datasets", description="Dataset collection name")
    dataset_version: str = Field(CURRENT_DATASET_VERSION, description="Release version of the dataset")
    schema_version: str = Field(CURRENT_SCHEMA_VERSION, description="Schema version used by release")
    release_status: str = Field("draft", description="Release status (draft/rc/approved_release)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    record_counts: RecordCountSummaryV1 = Field(..., description="Breakdown of record counts")
    files: List[ReleaseFileEntryV1] = Field(default_factory=list, description="List of published files and SHA-256 hashes")
    included_languages: List[str] = Field(default_factory=lambda: ["en"], description="Languages included in release")
    research_eligibility_status: str = Field("not_assessed", description="Dataset-level research eligibility")
    source_release: Optional[str] = Field(None, description="Parent or base release")
    generator_version: str = Field("stage14_generator_v1", description="Generator script version")

    @model_validator(mode="after")
    def validate_manifest_counts(self):
        calculated_total = (
            self.record_counts.adaptation_activities
            + self.record_counts.simplification_pairs
            + self.record_counts.lexicon_entries
        )
        if self.record_counts.total_reusable_records != calculated_total:
            raise ValueError(
                f"total_reusable_records ({self.record_counts.total_reusable_records}) "
                f"must equal sum of layer counts ({calculated_total})"
            )
        return self
