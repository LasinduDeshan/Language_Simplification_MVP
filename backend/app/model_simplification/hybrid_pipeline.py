"""
Stage 26: Hybrid Simplification Pipeline.
Coordinates generative model invocation, native validation, controlled surface repair,
revalidation, and transparent attributed deterministic fallback.
"""

import time
from typing import Dict, Optional, Any
from .schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    NativeValidationSummary,
    SupportLevel as S26SupportLevel,
    ProviderType
)
from .adapters.gemini_adapter import GeminiModelAdapter
from .adapters.mt5_adapter import Mt5ModelAdapter
from .adapters.mbart_adapter import MbartModelAdapter
from .adapters.stage25_adapter import Stage25ModelAdapter
from .controlled_surface_repair import apply_controlled_surface_repair
from .hmac_answer_guard import HmacAnswerGuard
from app.controlled_simplification.engine import ControlledSimplificationEngine
from app.controlled_simplification.schemas import (
    SimplificationRequest,
    SupportLevel as S25SupportLevel,
    ProtectedElementsConfig as S25ProtectedElementsConfig
)


class HybridSimplificationPipeline:
    """
    Hybrid coordinator orchestrating:
    Provider Candidate -> Stage 25 Validation -> Surface Repair -> Revalidation -> Fallback
    """
    def __init__(self):
        self.gemini_adapter = GeminiModelAdapter()
        self.mt5_adapter = Mt5ModelAdapter()
        self.mbart_adapter = MbartModelAdapter()
        self.stage25_adapter = Stage25ModelAdapter()
        self.stage25_engine = ControlledSimplificationEngine()
        self.answer_guard = HmacAnswerGuard()

    def process(self, request: ModelGenerationRequest, provider: ProviderType = ProviderType.GEMINI) -> ModelGenerationResult:
        start_time = time.perf_counter()

        # Select adapter
        if provider == ProviderType.GEMINI:
            adapter = self.gemini_adapter
        elif provider == ProviderType.MT5:
            adapter = self.mt5_adapter
        elif provider == ProviderType.MBART:
            adapter = self.mbart_adapter
        else:
            adapter = self.stage25_adapter

        # 1. Dispatch to model adapter
        provider_failure = False
        try:
            gen_res = adapter.generate(request)
            candidate_text = gen_res.candidate_text
        except Exception as e:
            provider_failure = True
            candidate_text = ""
            gen_res = ModelGenerationResult(
                request_id=request.request_id,
                requested_provider=provider.value,
                configured_model=str(provider.value),
                resolved_model=str(provider.value),
                model_resolution_status="failed",
                provider_calls_attempted=1,
                provider_outputs_received=0,
                candidate_text="",
                latency_ms=(time.perf_counter() - start_time) * 1000.0,
                native_validation=NativeValidationSummary(
                    disposition="provider_unavailable",
                    failed_gates=["VAL_PROVIDER_AVAILABILITY"],
                    warnings=[str(e)]
                ),
                metrics_attributed_to="controlled_stage25",
                generator_method=f"{provider.value}_failed",
                status="provider_failed"
            )

        # If terminal provider failure, trigger transparent Stage 25 fallback
        if provider_failure or not candidate_text:
            fallback_res = self._execute_stage25_fallback(request)
            gen_res.fallback_used = True
            gen_res.fallback_text = fallback_res.simplified_text
            gen_res.fallback_provider = "controlled_stage25"
            gen_res.metrics_attributed_to = "controlled_stage25"
            gen_res.candidate_text = fallback_res.simplified_text
            return gen_res

        # 2. Server-side HMAC answer non-disclosure verification
        leaked, leaked_ans = self.answer_guard.check_leakage(
            candidate_text,
            request.protected_elements.protected_answers
        )
        if leaked:
            # Critical answer breach: reject and trigger fallback
            gen_res.native_validation = NativeValidationSummary(
                disposition="rejected",
                failed_gates=["VAL_ANSWER_BOUNDARY"],
                warnings=[f"Protected answer tokens leaked: {leaked_ans}"]
            )
            fallback_res = self._execute_stage25_fallback(request)
            gen_res.fallback_used = True
            gen_res.fallback_text = fallback_res.simplified_text
            gen_res.fallback_provider = "controlled_stage25"
            gen_res.metrics_attributed_to = "controlled_stage25"
            return gen_res

        # 3. Stage 25 Full 12-Gate Meaning & Safety Validation
        s25_level = S25SupportLevel(request.support_level.value)
        val_res = self.stage25_engine.validate_custom_output(
            source_text=request.text,
            simplified_text=candidate_text,
            target_support_level=s25_level,
            caller_protected_elements=request.protected_elements.exact_preservation
        )

        disp = "passed" if val_res.all_critical_passed else ("rejected" if any("critical" in v.lower() or "violation" in v.lower() for v in val_res.detected_violations) else "manual_review_required")
        sim_score = val_res.advisory_semantic_similarity.similarity_score if (hasattr(val_res, "advisory_semantic_similarity") and val_res.advisory_semantic_similarity) else None

        gen_res.native_validation = NativeValidationSummary(
            disposition=disp,
            failed_gates=val_res.detected_violations,
            similarity_score=sim_score,
            warnings=val_res.detected_violations
        )

        # 4. Controlled Surface Repair if minor flaws detected
        if disp in ["manual_review_required", "passed_with_rollback"]:
            repaired_text, changed = apply_controlled_surface_repair(candidate_text)
            if changed:
                gen_res.controlled_repair_applied = True
                gen_res.repaired_text = repaired_text
                
                # Revalidate repaired text
                re_val = self.stage25_engine.validate_custom_output(
                    source_text=request.text,
                    simplified_text=repaired_text,
                    target_support_level=s25_level,
                    caller_protected_elements=request.protected_elements.exact_preservation
                )
                re_disp = "passed" if re_val.all_critical_passed else "manual_review_required"
                gen_res.revalidated_disposition = re_disp
                if re_disp == "passed":
                    gen_res.candidate_text = repaired_text
                    gen_res.metrics_attributed_to = "hybrid_validated"

        # 5. If terminal validation is rejected, trigger fallback
        if gen_res.native_validation.disposition == "rejected" and gen_res.revalidated_disposition != "passed":
            fallback_res = self._execute_stage25_fallback(request)
            gen_res.fallback_used = True
            gen_res.fallback_text = fallback_res.simplified_text
            gen_res.fallback_provider = "controlled_stage25"
            gen_res.metrics_attributed_to = "controlled_stage25"

        return gen_res

    def _execute_stage25_fallback(self, request: ModelGenerationRequest):
        s25_level = S25SupportLevel(request.support_level.value)
        s25_req = SimplificationRequest(
            request_id=f"FB-{request.request_id}",
            text=request.text,
            target_support_level=s25_level,
            provided_protected_elements=S25ProtectedElementsConfig(
                exact_preservation=request.protected_elements.exact_preservation
            )
        )
        return self.stage25_engine.simplify(s25_req)
