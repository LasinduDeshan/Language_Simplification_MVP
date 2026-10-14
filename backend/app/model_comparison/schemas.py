"""
Pydantic Schemas and Enums for Stage 28A Model Comparison.
Strictly defines mutually exclusive attribution, governance, and audit ledgers.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ExecutionCategory(str, Enum):
    DETERMINISTIC_REFERENCE = "deterministic_reference"
    DETERMINISTIC_BASELINE = "deterministic_baseline"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"
    CONTROLLED_RULES = "controlled_rules"
    LIVE_EXTERNAL_LLM = "live_external_llm"
    GOVERNED_HYBRID = "governed_hybrid"
    LOCAL_TRANSFORMER = "local_transformer"


class SystemEvaluationStatus(str, Enum):
    REGISTERED_AND_EVALUATED = "REGISTERED_AND_EVALUATED"
    NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS = "NOT_EVALUATED_0_VALID_NATIVE_OUTPUTS"
    NOT_EVALUATED_CHECKPOINT_MISSING = "NOT_EVALUATED_CHECKPOINT_MISSING"
    NOT_EVALUATED_UNSUPPORTED = "NOT_EVALUATED_UNSUPPORTED"


class DeliveryDisposition(str, Enum):
    """
    Mutually exclusive final delivery categories.
    Every logical item must resolve to exactly one category:
    Expected = NativeUnmodifiedDelivered + NativeRepairedDelivered +
               SafetyFallbackDelivered + ProviderFallbackDelivered +
               Failed + NotAttempted + Unaccounted
    """
    NATIVE_UNMODIFIED_DELIVERED = "NativeUnmodifiedDelivered"
    NATIVE_REPAIRED_DELIVERED = "NativeRepairedDelivered"
    SAFETY_FALLBACK_DELIVERED = "SafetyFallbackDelivered"
    PROVIDER_FALLBACK_DELIVERED = "ProviderFallbackDelivered"
    FAILED = "Failed"
    NOT_ATTEMPTED = "NotAttempted"
    UNACCOUNTED = "Unaccounted"


class GovernanceMetadata(BaseModel):
    evaluation_phase: str = "stage_28a_preliminary_automated_comparison"
    expert_validated: bool = False
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True
    stage27_human_validation_status: str = "pending"
    release_0_3_0_used: bool = False
    governance_statement: str = (
        "Stage 28A compares English simplification methods using automated metrics, "
        "frozen historical references, safety-oriented validation gates, and an external benchmark. "
        "Human expert suitability and child-delivery appropriateness have not yet been established."
    )


class DynamicProviderMetadata(BaseModel):
    requested_model: str
    resolved_model: str
    exact_api_returned_identifier: str = "models/gemini-3.5-flash-lite"
    internal_configuration_version: str = "stage28a-gemini-3.5-flash-lite-07-2026"
    discovery_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models"
    discovery_timestamp: str
    raw_metadata_response_hash: str


class PricingSnapshot(BaseModel):
    billing_surface: str
    source_url_or_snapshot: str
    retrieval_timestamp: str
    currency: str = "USD"
    units: str = "per_million_tokens"
    input_price_per_million_tokens: float
    output_price_per_million_tokens: float
    pricing_snapshot_sha256: str


class RegisteredSystem(BaseModel):
    system_id: str
    name: str
    execution_category: ExecutionCategory
    evaluation_status: SystemEvaluationStatus
    model_identifier: Optional[str] = None
    is_active_candidate: bool = True
    notes: str = ""


class ComparisonItemInput(BaseModel):
    item_id: str
    source_group_id: str
    source_text: str
    support_level: str
    target_age: int = 6
    protected_terms: List[str] = Field(default_factory=list)
    reference_texts: List[str] = Field(default_factory=list)
    dataset_name: str  # internal_locked_full, internal_locked_clean, asset_test


class ItemExecutionLedgerRecord(BaseModel):
    evaluation_item_id: str
    source_group_id: str
    support_level: str
    requested_system: str
    requested_model: Optional[str] = None
    resolved_model: Optional[str] = None
    provider_model_version: Optional[str] = None
    internal_configuration_version: Optional[str] = "stage28a-gemini-3.5-flash-lite-07-2026"
    discovery_timestamp: Optional[str] = None
    generator_attribution: str
    final_disposition: DeliveryDisposition
    native_output_received: bool = False
    repair_used: bool = False
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    http_status: Optional[int] = None
    attempt_count: int = 1
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    currency: str = "USD"
    pricing_source: Optional[str] = None
    pricing_snapshot_date: Optional[str] = None
    pricing_snapshot_sha256: Optional[str] = None
    input_price_per_million_tokens: Optional[float] = None
    output_price_per_million_tokens: Optional[float] = None
    free_tier_usage: bool = True
    estimated_billable_cost: float = 0.0
    output_text: Optional[str] = None  # Protected: only in internal ledger
    output_sha256: Optional[str] = None
    validation_status: str = "passed"
    raw_error: Optional[str] = None


class AccountingSummary(BaseModel):
    expected_items: int
    native_unmodified_delivered: int
    native_repaired_delivered: int
    safety_fallback_delivered: int
    provider_fallback_delivered: int
    failed: int
    not_attempted: int
    unaccounted: int
    duplicates: int = 0
    missing_items: int = 0

    @property
    def total_delivered(self) -> int:
        return (
            self.native_unmodified_delivered
            + self.native_repaired_delivered
            + self.safety_fallback_delivered
            + self.provider_fallback_delivered
        )

    @property
    def total_accounted(self) -> int:
        return (
            self.total_delivered
            + self.failed
            + self.not_attempted
            + self.unaccounted
        )

    @property
    def is_strictly_conserved(self) -> bool:
        return (
            self.total_accounted == self.expected_items
            and self.duplicates == 0
            and self.missing_items == 0
            and self.unaccounted == 0
        )
