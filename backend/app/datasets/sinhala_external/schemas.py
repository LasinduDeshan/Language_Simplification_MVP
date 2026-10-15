"""
Pydantic v2 schemas for Stage 31 Sinhala External Dataset Ingestion.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PrimarySourceDecision(str, Enum):
    APPROVED = "APPROVED"
    METADATA_ONLY = "METADATA_ONLY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"

class RobotsTxtStatus(str, Enum):
    PERMITTED = "PERMITTED"
    DISALLOWED = "DISALLOWED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNAVAILABLE_REVIEW_REQUIRED = "UNAVAILABLE_REVIEW_REQUIRED"

class AcquisitionPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_method: str = Field(..., description="direct_download | web_crawl | api")
    robots_txt_status: RobotsTxtStatus = Field(..., description="Robots compliance enum")
    robots_txt_checked_at: Optional[str] = None
    crawl_delay_seconds: Optional[float] = None

class SourcePermissions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    internal_research_use_allowed: bool
    download_allowed: bool
    local_storage_allowed: bool
    modification_allowed: bool
    derived_processing_allowed: bool
    raw_redistribution_allowed: bool
    derived_text_redistribution_allowed: bool
    commercial_use_allowed: bool
    attribution_required: bool
    share_alike_required: bool

class CandidateSourceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str
    source_name: str
    publisher: str
    canonical_url_sanitized: str
    source_class: str
    language_claim: str
    primary_decision: PrimarySourceDecision
    licence_name: Optional[str] = None
    licence_version: Optional[str] = None
    licence_url_sanitized: Optional[str] = None
    terms_url_sanitized: Optional[str] = None
    rights_profile_id: str
    rights_profile_version: int = 1
    supersedes_version: Optional[int] = None
    rights_profile_effective_at: Optional[str] = None
    rights_profile_review_due_at: Optional[str] = None
    rights_evidence_sha256: Optional[str] = None
    acquisition_policy: AcquisitionPolicy
    permissions: SourcePermissions
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    notes: Optional[str] = None

class SanitizedAcquisitionReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    retrieval_id: str
    source_id: str
    retrieved_at: str
    retrieval_method: str
    resolved_url_sanitized: str
    redirect_chain_sanitized: List[str] = Field(default_factory=list)
    sensitive_query_parameters_removed: bool = True
    http_status: int = 200
    content_type: str
    file_name: str
    byte_size: int
    sha256: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    raw_storage_ref: str
    redistribution_allowed: bool

    @field_validator("raw_storage_ref")
    @classmethod
    def validate_storage_ref(cls, v: str) -> str:
        if not v.startswith("protected://"):
            raise ValueError(f"raw_storage_ref must use abstract protected:// URI, got: {v}")
        return v

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError(f"sha256 must be a 64-character hex string, got: {v}")
        return v.lower()

class ParsingStatus(str, Enum):
    PARSED = "PARSED"
    SKIPPED_BY_POLICY = "SKIPPED_BY_POLICY"
    PARSE_FAILED = "PARSE_FAILED"
    QUARANTINED = "QUARANTINED"

class StagedDocumentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str
    source_id: str
    retrieval_id: str
    rights_profile_id: str
    rights_profile_version: int = 1
    raw_file_sha256: str
    source_document_key: str
    document_group_id: str
    source_offset_or_locator: str
    authoring_origin: str = "human_authored_claimed"
    is_method_development_unit: bool = False
    provisional_domain: str = "unclassified_provisional"
    parsing_status: ParsingStatus = ParsingStatus.PARSED
    raw_text_storage_ref: str

    @field_validator("raw_text_storage_ref")
    @classmethod
    def validate_storage_ref(cls, v: str) -> str:
        if not v.startswith("protected://"):
            raise ValueError(f"raw_text_storage_ref must use abstract protected:// URI, got: {v}")
        return v

    @field_validator("source_offset_or_locator")
    @classmethod
    def validate_safe_locator(cls, v: str) -> str:
        # Enforce Invariant 6: locator must not leak private paths, credentials, or keys
        forbidden_patterns = [r"[a-zA-Z]:\\", r"\/Users\/", r"\/home\/", r"token=", r"key=", r"password="]
        for pat in forbidden_patterns:
            import re
            if re.search(pat, v, re.IGNORECASE):
                raise ValueError(f"source_offset_or_locator leaks host path or credential: {v}")
        return v

class CorpusSplit(str, Enum):
    TRAIN = "train"
    VALIDATION = "validation"
    LOCKED_TEST = "locked_test"

class SplitComponentType(str, Enum):
    TRAIN_ONLY_DEVELOPMENT_COMPONENT = "TRAIN_ONLY_DEVELOPMENT_COMPONENT"
    UNTOUCHED_EVAL_ELIGIBLE_COMPONENT = "UNTOUCHED_EVAL_ELIGIBLE_COMPONENT"

class PilotCorpusRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_id: str
    document_id: str
    source_id: str
    all_contributing_sources: List[str]
    retrieval_id: str
    rights_profile_id: str
    rights_profile_version: int = 1
    public_record_digest: str
    hmac_key_id: str
    hmac_key_version: int
    digest_input_schema: str
    split: CorpusSplit
    split_group_id: str
    component_type: SplitComponentType
    document_group_id: str
    source_offset_or_locator: str
    provisional_domain: str
    authoring_origin: str = "human_authored_claimed"
    is_method_development_record: bool
    stage30_disposition: str
    stage30_configuration_hash: str
    stage31_configuration_hash: str
    normalized_text_storage_ref: str
    sentence_count: int
    token_count: int
    grapheme_count: int
    quality_flags: List[str]
    effective_export_policy: str
    literal_text_redistributable: bool
    canonical_record_id: str
    is_canonical_exact_record: bool = True
    exact_duplicate_weight: float = 1.0
    retention_reason: str = "PRIMARY_CANONICAL_RECORD"

    @field_validator("normalized_text_storage_ref")
    @classmethod
    def validate_storage_ref(cls, v: str) -> str:
        if not v.startswith("protected://"):
            raise ValueError(f"normalized_text_storage_ref must use abstract protected:// URI, got: {v}")
        return v
