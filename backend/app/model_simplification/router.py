"""
Stage 26 Model Router.
Routes simplification requests to configured adapters (Gemini, mT5, mBART, Stage 25 deterministic, or Hybrid)
and integrates hybrid deterministic validation and safety fallbacks.
"""
from typing import Dict, Any, Optional, List
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.model_simplification.adapters.stage25_adapter import Stage25ControlledAdapter
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter
from app.model_simplification.adapters.mt5_adapter import MT5ModelAdapter
from app.model_simplification.adapters.mbart_adapter import MBARTModelAdapter
from app.model_simplification.hybrid_pipeline import HybridValidationPipeline
from app.model_simplification.privacy_filter import PrivacyFilter


class ModelRouter:
    """
    Router dispatching generation requests to candidate models and applying hybrid validation.
    """

    def __init__(
        self,
        gemini_adapter: Optional[GeminiModelAdapter] = None,
        mt5_adapter: Optional[MT5ModelAdapter] = None,
        mbart_adapter: Optional[MBARTModelAdapter] = None,
        stage25_adapter: Optional[Stage25ControlledAdapter] = None,
        hybrid_pipeline: Optional[HybridValidationPipeline] = None,
    ):
        self.stage25_adapter = stage25_adapter or Stage25ControlledAdapter()
        self.gemini_adapter = gemini_adapter or GeminiModelAdapter(fallback_adapter=self.stage25_adapter)
        self.mt5_adapter = mt5_adapter or MT5ModelAdapter(fallback_adapter=self.stage25_adapter)
        self.mbart_adapter = mbart_adapter or MBARTModelAdapter(fallback_adapter=self.stage25_adapter)
        self.hybrid_pipeline = hybrid_pipeline or HybridValidationPipeline()
        self.privacy_filter = PrivacyFilter()

    def route_and_generate(
        self,
        request: ModelGenerationRequest,
        model_id: str = "gemini-1.5-flash-prompted",
        protected_answers: Optional[List[str]] = None,
    ) -> ModelGenerationResult:
        """
        Sanitizes request, dispatches to adapter, applies hybrid Stage 25 validation,
        and returns validated ModelGenerationResult.
        """
        # 1. Sanitize request
        clean_req = self.privacy_filter.sanitize_request({}, request)

        # 2. Dispatch to selected adapter
        model_key = model_id.lower()
        if "gemini" in model_key or "google" in model_key:
            res = self.gemini_adapter.generate(clean_req, protected_answers=protected_answers)
        elif "mt5" in model_key:
            res = self.mt5_adapter.generate(clean_req)
        elif "mbart" in model_key:
            res = self.mbart_adapter.generate(clean_req)
        elif "stage25" in model_key or "rule" in model_key:
            res = self.stage25_adapter.generate(clean_req)
        elif "hybrid" in model_key:
            # Hybrid: Gemini first, validate with Stage 25, fallback if invalid
            gemini_res = self.gemini_adapter.generate(clean_req, protected_answers=protected_answers)
            if not gemini_res.fallback_used and gemini_res.candidate_text:
                disp, failed_gates, repairs, final_text, sim = self.hybrid_pipeline.validate_candidate(
                    clean_req, gemini_res.candidate_text, protected_answers=protected_answers
                )
                if disp in {NativeValidationDisposition.PASSED, NativeValidationDisposition.PASSED_WITH_CONTROLLED_REPAIR}:
                    gemini_res.candidate_text = final_text
                    gemini_res.native_validation = NativeValidationSummary(
                        disposition=disp,
                        failed_gates=failed_gates,
                        similarity_score=sim,
                        repair_operations_applied=repairs,
                    )
                    return gemini_res
            # If Gemini failed or rejected by hybrid validation, route to Stage 25 fallback
            fb_res = self.stage25_adapter.generate(clean_req)
            fb_res.fallback_used = True
            fb_res.fallback_provider = "stage25_rule_engine"
            fb_res.execution_status = ExecutionStatus.STAGE25_FALLBACK
            return fb_res
        else:
            # Default to Stage 25 deterministic
            res = self.stage25_adapter.generate(clean_req)

        # 3. Apply hybrid deterministic validation if not already evaluated
        if not res.fallback_used and res.candidate_text:
            disp, failed_gates, repairs, final_text, sim = self.hybrid_pipeline.validate_candidate(
                clean_req, res.candidate_text, protected_answers=protected_answers
            )
            res.candidate_text = final_text
            res.native_validation = NativeValidationSummary(
                disposition=disp,
                failed_gates=failed_gates,
                similarity_score=sim,
                repair_operations_applied=repairs,
            )

        return res
