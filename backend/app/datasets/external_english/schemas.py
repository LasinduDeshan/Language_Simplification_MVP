"""Pydantic v2 schemas for Stage 23 External English Dataset Integration and Governance."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

ExternalDatasetId = Literal[
    "EXTDATA-ASSET",
    "EXTDATA-TURKCORPUS",
    "EXTDATA-OASISSIMP-EN",
    "EXTDATA-WIKILARGE-PILOT",
    "EXTDATA-NEWSELA",
]

RightsStatus = Literal[
    "pending_content_rights_verification",
    "approved_local_research",
    "approved_public_research",
    "excluded_rights",
    "pending_lineage_and_rights_verification",
]

FinalDispositionType = Literal[
    "quarantined_safety",
    "excluded_rights",
    "excluded_schema",
    "excluded_leakage",
    "excluded_quality",
    "excluded_age_domain",
    "manual_review_required",
    "benchmark_only",
    "training_candidate",
]

ExternalDatasetAction = Literal[
    "acquire",
    "local_process",
    "benchmark",
    "train",
    "redistribute_raw",
    "redistribute_normalized",
    "release_features",
]

IntendedUseContext = Literal[
    "noncommercial_academic_research",
    "commercial_deployment",
    "unspecified",
]


class DatasetPermissions(BaseModel):
    """Granular permissions evaluated for external dataset content."""

    model_config = ConfigDict(extra="forbid")

    local_processing_allowed: bool = Field(default=False)
    redistribution_allowed: bool = Field(default=False)
    benchmark_use_allowed: bool = Field(default=False)
    training_use_allowed: bool = Field(default=False)
    derived_feature_release_allowed: bool = Field(default=False)


class RightsEvidence(BaseModel):
    """Primary evidence documenting legal rights and licensing terms."""

    model_config = ConfigDict(extra="forbid")

    evidence_type: Literal[
        "dataset_license_file",
        "paper_statement",
        "repository_terms",
        "quarantined_inspection",
        "direct_communication",
    ] = "dataset_license_file"
    evidence_url: Optional[str] = None
    commit_sha: Optional[str] = None
    evidence_sha256: Optional[str] = None
    evidence_scope: Literal["dataset_content", "repository_software", "mixed_lineage", "unverified"] = "unverified"
    verified_licence_identifier: Optional[str] = None
    permission_rationale: str = ""
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    
    # Intended use context and compliance conditions
    intended_use_context: str = "noncommercial_academic_research"
    commercial_use_allowed: bool = False
    requires_attribution: bool = True
    requires_share_alike: bool = False
    licence_notice_required: bool = True
    noncommercial_only: bool = True


class ExternalDatasetRegistryRecord(BaseModel):
    """Registry record specifying source metadata, multi-layer licences, and evaluated rights status."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: ExternalDatasetId
    dataset_name: str
    official_source_url: str
    publication_reference: str
    content_licence_name: Optional[str] = None
    content_licence_url: Optional[str] = None
    
    # Multi-layer licensing breakdown
    repository_code_licence: Optional[str] = None
    source_text_licence: Optional[str] = None
    crowdsourced_references_licence: Optional[str] = None
    dataset_collection_terms: Optional[str] = None

    rights_status: RightsStatus = "pending_content_rights_verification"
    permissions: DatasetPermissions = Field(default_factory=DatasetPermissions)
    evidence: Optional[RightsEvidence] = None
    notes: Optional[str] = None


class RightsDecision(BaseModel):
    """Formal rights gate decision for a dataset candidate."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: ExternalDatasetId
    rights_status: RightsStatus
    permissions: DatasetPermissions
    evidence: Optional[RightsEvidence] = None
    evidence_summary: str
    verified_by: str
    verified_at: datetime


class DualTextRecord(BaseModel):
    """Preserves raw text alongside derived evaluation view without mutating official benchmark."""

    model_config = ConfigDict(extra="forbid")

    raw_source_text: str
    raw_references: List[str] = Field(default_factory=list)
    evaluation_source_text: str
    evaluation_references: List[str] = Field(default_factory=list)
    raw_text_preserved: bool = True
    evaluation_view_derived: bool = True
    normalization_operations: List[str] = Field(default_factory=lambda: ["nfc_unicode_normalization"])
    official_benchmark_files_overwritten: bool = False


class NormalizedExternalRecord(BaseModel):
    """Canonical multi-reference external record schema adhering to Stage 14/23 standards."""

    model_config = ConfigDict(extra="forbid")

    external_record_id: str
    schema_version: str = "1.0.0"
    dataset_id: ExternalDatasetId
    dataset_record_id: str
    source_group_id: str
    
    # Dual representation text content
    raw_source_text: str
    raw_references: List[str] = Field(default_factory=list)
    evaluation_source_text: str
    evaluation_references: List[str] = Field(default_factory=list)
    raw_text_preserved: bool = True
    evaluation_view_derived: bool = True
    normalization_operations: List[str] = Field(default_factory=lambda: ["nfc_unicode_normalization"])
    official_benchmark_files_overwritten: bool = False
    
    reference_count: int = Field(ge=1)
    language: str = "en"
    source_domain: str = "wikipedia_general"
    original_source_split: Literal["train", "validation", "test", "pilot"] = "test"
    content_hash: str
    preprocessing_version: str = "1.0.0"
    
    # Quality & suitability statuses
    quality_disposition: Literal["passed", "failed", "manual_review_required"] = "passed"
    age_domain_status: Literal[
        "not_verified",
        "potentially_age_appropriate",
        "general_domain_benchmark",
        "adult_or_advanced_topic",
        "manual_age_review_required",
        "excluded_age_domain",
    ] = "general_domain_benchmark"
    
    # Benchmark isolation and governance locks
    evaluation_protected: bool = True
    protection_reason: Optional[str] = "external_benchmark_source"
    expert_dld_validated: bool = False
    approved_for_child_delivery: bool = False
    research_eligible: bool = False
    training_eligible: bool = False
    benchmark_eligible: bool = True
    
    final_disposition: FinalDispositionType = "benchmark_only"
    
    provenance: Dict[str, Any] = Field(default_factory=dict)
    quality_metrics: Optional[Dict[str, Any]] = None
    suitability_metrics: Optional[Dict[str, Any]] = None


class ExternalDispositionRecord(BaseModel):
    """Record summary tracking dual-level disposition for a source group and its references."""

    model_config = ConfigDict(extra="forbid")

    source_group_id: str
    external_record_id: str
    dataset_id: ExternalDatasetId
    source_group_disposition: FinalDispositionType
    reference_dispositions: List[FinalDispositionType]
    disposition_rationale: str
    is_evaluation_protected: bool
