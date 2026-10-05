"""
Stage 26: Stage 25 Deterministic Model Adapter & Fallback Generator.
Wraps the frozen Stage 25 engine (from stage-25-complete-v2) under the common adapter interface.
"""

import time
from typing import Optional
from ..schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    NativeValidationSummary,
    SupportLevel as S26SupportLevel
)
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel as S25SupportLevel,
    ProtectedElementsConfig as S25ProtectedElementsConfig
)


class Stage25ModelAdapter:
    """
    Adapter for the Stage 25 Deterministic Controlled Simplification Engine.
    Used both as a frozen baseline comparator and as the transparent fallback engine.
    """
    def __init__(self):
        self.engine = ControlledSimplificationEngine()
        self.model_id = "controlled_stage25"

    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResult:
        start_time = time.perf_counter()
        
        # Map support level
        level_map = {
            S26SupportLevel.MILD: S25SupportLevel.MILD,
            S26SupportLevel.MODERATE: S25SupportLevel.MODERATE,
            S26SupportLevel.STRONG: S25SupportLevel.STRONG
        }
        s25_level = level_map.get(request.support_level, S25SupportLevel.MODERATE)

        s25_req = SimplificationRequest(
            request_id=request.request_id,
            text=request.text,
            target_support_level=s25_level,
            provided_protected_elements=S25ProtectedElementsConfig(
                exact_preservation=request.protected_elements.exact_preservation
            )
        )

        resp = self.engine.simplify(s25_req)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        val_summary = NativeValidationSummary(
            disposition=resp.status.value,
            failed_gates=resp.validation_results.detected_violations if hasattr(resp.validation_results, "detected_violations") else [],
            similarity_score=resp.validation_results.advisory_semantic_similarity.similarity_score if (hasattr(resp.validation_results, "advisory_semantic_similarity") and resp.validation_results.advisory_semantic_similarity) else None,
            warnings=resp.validation_results.detected_violations if hasattr(resp.validation_results, "detected_violations") else []
        )

        return ModelGenerationResult(
            request_id=request.request_id,
            requested_provider="controlled_stage25",
            configured_model="controlled_stage25:1.0.0",
            resolved_model="controlled_stage25:1.0.0",
            model_resolution_status="verified",
            provider_calls_attempted=1,
            provider_outputs_received=1,
            candidate_text=resp.simplified_text,
            latency_ms=elapsed_ms,
            input_token_count=len(request.text.split()),
            output_token_count=len(resp.simplified_text.split()),
            estimated_cost_usd=0.0,
            native_validation=val_summary,
            controlled_repair_applied=resp.status.value == "PASSED_WITH_ROLLBACK",
            repaired_text=resp.simplified_text if resp.status.value == "PASSED_WITH_ROLLBACK" else None,
            revalidated_disposition=resp.status.value if resp.status.value == "PASSED_WITH_ROLLBACK" else None,
            fallback_used=False,
            fallback_text=None,
            fallback_provider=None,
            metrics_attributed_to="controlled_stage25",
            generator_method="controlled_stage25",
            prompt_template_version="N/A",
            status="candidate_generated"
        )
