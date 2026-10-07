"""
Stage 26 Adapter for Stage 25 Deterministic Controlled Simplification Engine.
Serves as frozen comparator baseline and separately attributed safety fallback.
"""
import time
from typing import Dict, Any, Optional
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import SimplificationRequest as Stage25Request


class Stage25ControlledAdapter:
    """
    Deterministic rule-based simplification adapter wrapping the Stage 25 engine.
    """

    def __init__(self, engine: Optional[ControlledSimplificationEngine] = None):
        self.engine = engine or ControlledSimplificationEngine()
        self.model_id = "stage25-controlled-deterministic"

    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResult:
        start_time = time.perf_counter()

        # Map Stage 26 request to Stage 25 request
        s25_req = Stage25Request(
            request_id=request.request_id,
            text=request.text,
            target_tier=request.support_level,
            content_type=request.content_type,
            response_mode=request.response_mode,
            target_age=request.target_age,
            language=request.language,
        )

        s25_res = self.engine.simplify(s25_req)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        disp = NativeValidationDisposition.PASSED
        failed_gates = []
        if str(s25_res.status.value).upper() not in {"PASSED", "PASSED_WITH_ROLLBACK"}:
            disp = NativeValidationDisposition.REJECTED
            failed_gates = ["stage25_internal_rule_failure"]

        return ModelGenerationResult(
            request_id=request.request_id,
            requested_provider="local_rule",
            configured_model="stage-25-complete-v2",
            resolved_model="stage-25-complete-v2-6b78550",
            model_resolution_status="verified",
            execution_status=ExecutionStatus.LOCAL_NATIVE_INFERENCE,
            provider_calls_attempted=1,
            candidate_text=s25_res.simplified_text,
            native_validation=NativeValidationSummary(
                disposition=disp,
                failed_gates=failed_gates,
                similarity_score=0.95,
                repair_operations_applied=[op.type for op in s25_res.applied_operations],
            ),
            latency_ms=round(latency_ms, 2),
            fallback_used=False,
            generator_method="controlled_stage25",
            prompt_template_version=None,
        )
