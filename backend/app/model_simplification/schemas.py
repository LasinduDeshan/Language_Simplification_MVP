"""
Stage 26: Model Simplification Schemas and DTOs.
Separates runtime generation DTOs from batch evaluation metric DTOs.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    GEMINI = "gemini"
    MT5 = "mt5"
    MBART = "mbart"
    STAGE25 = "controlled_stage25"


class GeneratorMethod(str, Enum):
    PRETRAINED_ZERO_SHOT = "pretrained_zero_shot"
    PRETRAINED_PROMPT_PREFIX = "pretrained_prompt_prefix"
    FINE_TUNED_INTERNAL_ELIGIBLE = "fine_tuned_internal_eligible"
    GEMINI_PROMPTED = "gemini_prompted"
    HYBRID_VALIDATED = "hybrid_validated"
    CONTROLLED_STAGE25 = "controlled_stage25"


class SupportLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"


class ValidationDisposition(str, Enum):
    PASSED = "passed"
    REPAIR_PASSED = "repair_passed"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    REJECTED = "rejected"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    FALLBACK_GENERATED = "fallback_generated"


class ProtectedElements(BaseModel):
    exact_preservation: List[str] = Field(default_factory=list, description="Entities, terms, quantities to preserve exactly")
    semantic_equivalence_refs: List[str] = Field(default_factory=list, description="Opaque semantic reference IDs")
    protected_answers: List[str] = Field(default_factory=list, description="Server-side private answer tokens to prevent task leakage")
    answer_boundary_ref: Optional[str] = Field(None, description="Opaque server-side answer reference (NEVER sent to external models)")


class ModelGenerationRequest(BaseModel):
    request_id: str
    text: str
    language: str = "en"
    target_age: int = Field(default=6, ge=4, le=8)
    support_level: SupportLevel = SupportLevel.MODERATE
    content_type: str = "instruction"
    response_mode: str = "direct_action"
    protected_elements: ProtectedElements = Field(default_factory=ProtectedElements)
    action_graph_ref: Optional[str] = None
    generation_config_id: Optional[str] = None
    generation_constraints: Dict[str, Any] = Field(default_factory=dict)


class NativeValidationSummary(BaseModel):
    disposition: str
    failed_gates: List[str] = Field(default_factory=list)
    similarity_score: Optional[float] = None
    warnings: List[str] = Field(default_factory=list)


class ModelGenerationResult(BaseModel):
    request_id: str
    requested_provider: str
    configured_model: str
    resolved_model: str
    model_resolution_status: str = "verified"
    provider_calls_attempted: int = 1
    provider_outputs_received: int = 1
    candidate_text: str
    latency_ms: float = 0.0
    input_token_count: int = 0
    output_token_count: int = 0
    estimated_cost_usd: Optional[float] = None
    
    # Runtime Validation Summary
    native_validation: NativeValidationSummary
    
    # Controlled Surface Repair
    controlled_repair_applied: bool = False
    repaired_text: Optional[str] = None
    revalidated_disposition: Optional[str] = None
    
    # Transparent Fallback Attribution
    fallback_used: bool = False
    fallback_text: Optional[str] = None
    fallback_provider: Optional[str] = None
    metrics_attributed_to: str = "native_model"
    
    generator_method: str = "gemini_prompted"
    prompt_template_version: Optional[str] = "1.0.0"
    status: str = "candidate_generated"


class ModelEvaluationResult(BaseModel):
    evaluation_id: str
    generator_method: str
    support_level: str
    dataset_split: str
    sample_count: int
    sari_tier_matched: float
    sari_multi_reference: float
    sari_add: float
    sari_keep: float
    sari_del: float
    sacrebleu: float
    fkgl_delta: float
    exact_element_recall: float
    semantic_similarity_mean: float
    native_pass_rate: float
    repair_pass_rate: float
    manual_review_rate: float
    rejection_rate: float
    fallback_rate: float
    mean_latency_ms: float
    total_cost_usd: Optional[float] = None
