"""
Stage 26 Runtime Schemas and DTOs.
Strictly isolates runtime generation request/response data from aggregate benchmark metrics.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    LIVE_PROVIDER_INFERENCE = "live_provider_inference"
    LOCAL_NATIVE_INFERENCE = "local_native_inference"
    CACHED_NATIVE_OUTPUT = "cached_native_output"
    OFFLINE_FIXTURE = "offline_fixture"
    SIMULATED_ADAPTER = "simulated_adapter"
    IDENTITY_FALLBACK = "identity_fallback"
    STAGE25_FALLBACK = "stage25_fallback"
    NOT_EXECUTED = "not_executed"


class NativeValidationDisposition(str, Enum):
    PASSED = "passed"
    PASSED_WITH_CONTROLLED_REPAIR = "passed_with_controlled_repair"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    REJECTED = "rejected"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    FALLBACK_GENERATED = "fallback_generated"
    ADULT_SUPPORT_REQUIRED = "adult_support_required"


class ProtectedElementsDTO(BaseModel):
    exact_preservation: List[str] = Field(default_factory=list)
    semantic_equivalence_refs: List[str] = Field(default_factory=list)
    answer_boundary_ref: Optional[str] = None


class ModelGenerationRequest(BaseModel):
    request_id: str
    text: str
    language: str = "en"
    target_age: int = 6
    support_level: str  # mild, moderate, strong
    content_type: str = "instruction"
    response_mode: str = "direct_action"
    protected_elements: ProtectedElementsDTO = Field(default_factory=ProtectedElementsDTO)
    action_graph_ref: Optional[str] = None
    generation_config_id: Optional[str] = None


class NativeValidationSummary(BaseModel):
    disposition: NativeValidationDisposition
    failed_gates: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    repair_operations_applied: List[str] = Field(default_factory=list)


class ModelGenerationResult(BaseModel):
    request_id: str
    requested_provider: str
    configured_model: str
    resolved_model: str
    model_resolution_status: str = "verified"  # verified, smoke_tested, unverified, failed
    execution_status: ExecutionStatus
    provider_calls_attempted: int = 1
    candidate_text: str
    native_validation: Optional[NativeValidationSummary] = None
    latency_ms: float
    input_token_count: Optional[int] = None
    output_token_count: Optional[int] = None
    estimated_cost: Optional[float] = None
    fallback_used: bool = False
    fallback_provider: Optional[str] = None
    generator_method: str
    prompt_template_version: Optional[str] = None
    # Cached output provenance metadata
    original_execution_status: Optional[str] = None
    original_run_id: Optional[str] = None
    quality_metrics_permitted: bool = True
    current_latency_metrics_permitted: bool = True
    current_provider_reliability_metrics_permitted: bool = True
