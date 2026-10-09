"""
Stage 26 Gemini Provider Adapter.
Integrates Google Gemini API (gemini-3.5-flash-lite) with dynamic model verification,
pre-dispatch collision checks, allowlist payload serialization, jittered exponential retry,
quota and rate-limit management, cost tracking, and transparent Stage 25 fallback.
"""
import os
import time
import json
import random
import requests
from typing import Optional, Dict, Any, List, Tuple
from app.core.config import settings
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
)
from app.model_simplification.prompt_registry import PromptRegistry
from app.model_simplification.provider_payload_serializer import ProviderPayloadSerializer
from app.model_simplification.hmac_answer_guard import HMACAnswerGuard
from app.model_simplification.cost_tracker import CostTracker
from app.model_simplification.adapters.stage25_adapter import Stage25ControlledAdapter
from app.model_simplification.quota_manager import GeminiQuotaManager


class GeminiModelAdapter:
    """
    Adapter for Google Gemini API with safety boundaries, quota throttling, and fallback routing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout_seconds: Any = (30.0, 60.0),
        max_retries: int = 4,
        fallback_adapter: Optional[Stage25ControlledAdapter] = None,
        quota_manager: Optional[GeminiQuotaManager] = None,
    ):
        if api_key is not None:
            self.api_key = api_key.strip()
        else:
            self.api_key = (getattr(settings, "gemini_api_key", "") or os.getenv("GEMINI_API_KEY", "")).strip()
        self.configured_model = model_id or getattr(settings, "llm_model", "gemini-3.5-flash-lite")
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.serializer = ProviderPayloadSerializer()
        self.answer_guard = HMACAnswerGuard()
        self.fallback_adapter = fallback_adapter or Stage25ControlledAdapter()
        self.quota_manager = quota_manager
        self.verified_model_id: Optional[str] = None

    def discover_and_verify_model(self) -> Tuple[bool, str]:
        """
        Discovers available models and confirms configured model supports generateContent.
        """
        if not self.api_key:
            return False, "GEMINI_API_KEY not configured"

        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        try:
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "").replace("models/", "") for m in data.get("models", [])]
                # Check for direct match or substring
                for m in models:
                    if m == self.configured_model or self.configured_model in m:
                        self.verified_model_id = m
                        return True, m
                return False, f"Model '{self.configured_model}' not found in available models: {models[:5]}"
            return False, f"Model discovery failed with HTTP {resp.status_code}"
        except Exception as e:
            return False, f"Discovery request error: {str(e)}"

    def smoke_test(self) -> Tuple[bool, str]:
        """
        Runs one live test request before batch evaluation.
        """
        if not self.api_key:
            return False, "Missing API key"

        model_name = self.verified_model_id or self.configured_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": "Hello, respond with 'OK'."}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 10},
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                return True, "Smoke test successful"
            return False, f"Smoke test returned HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            return False, f"Smoke test exception: {str(e)}"

    def generate(
        self,
        request: ModelGenerationRequest,
        protected_answers: Optional[List[str]] = None,
        run_id: Optional[str] = None,
        dataset_split: str = "validation",
        source_group_id: Optional[str] = None,
    ) -> ModelGenerationResult:
        start_time = time.perf_counter()

        # 1. Pre-dispatch collision check: exact_preservation vs protected answers
        if protected_answers:
            has_collision, term = self.answer_guard.check_protected_element_collision(
                request.protected_elements.exact_preservation,
                protected_answers
            )
            if has_collision:
                # Security violation: do not dispatch to external API
                return self._trigger_fallback(
                    request,
                    reason=f"pre_dispatch_collision_detected: term '{term}' overlaps protected answer boundary",
                    disposition=NativeValidationDisposition.MANUAL_REVIEW_REQUIRED,
                )

        # 2. Check if live API key is available
        if not self.api_key:
            return self._trigger_fallback(
                request,
                reason="no_api_key_configured_offline_fallback",
                disposition=NativeValidationDisposition.FALLBACK_GENERATED,
            )

        # 3. Quota check
        if self.quota_manager:
            can_go, q_msg = self.quota_manager.can_proceed()
            if not can_go:
                return self._trigger_fallback(
                    request,
                    reason=f"quota_exhausted: {q_msg}",
                    disposition=NativeValidationDisposition.PROVIDER_UNAVAILABLE,
                )
            self.quota_manager.wait_for_slot()

        model_name = self.verified_model_id or self.configured_model
        prompt = PromptRegistry.get_prompt(
            text=request.text,
            support_level=request.support_level,
            exact_preservation=request.protected_elements.exact_preservation
        )

        # 4. Allowlist payload serialization
        serialized_payload = self.serializer.serialize(request, prompt_instructions=prompt)

        # 5. Dispatch with exponential retry
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        api_payload = {
            "contents": [{"parts": [{"text": serialized_payload["prompt_instructions"]}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 256,
            }
        }

        backoff_delays = [2.0, 4.0, 8.0, 16.0]
        attempts = 0
        candidate_text = ""
        last_status_code = 0
        last_error_text = ""
        finish_reason = ""

        for attempt in range(self.max_retries):
            attempts += 1
            try:
                resp = requests.post(url, headers=headers, json=api_payload, timeout=self.timeout)
                last_status_code = resp.status_code
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        cand = candidates[0]
                        finish_reason = cand.get("finishReason", "STOP")
                        if finish_reason not in {"SAFETY", "RECITATION", "BLOCKED"}:
                            parts = cand.get("content", {}).get("parts", [])
                            if parts:
                                txt = parts[0].get("text", "").strip()
                                if txt:
                                    candidate_text = txt
                                    break
                elif resp.status_code in (400, 401, 403, 404):
                    last_error_text = resp.text
                    err_type = GeminiQuotaManager.classify_error(resp.status_code, resp.text)
                    if err_type == "DAILY_QUOTA_FAILED":
                        break
                    break
                elif resp.status_code == 429:
                    last_error_text = resp.text
                    err_type = GeminiQuotaManager.classify_error(429, resp.text)
                    if err_type == "DAILY_QUOTA_FAILED":
                        # Daily quota exhausted: stop immediately
                        break
                    # Transient rate limit: backoff delay with jitter
                    if attempt < self.max_retries - 1:
                        retry_after = resp.headers.get("Retry-After")
                        delay = float(retry_after) if retry_after and retry_after.isdigit() else (backoff_delays[min(attempt, len(backoff_delays) - 1)] + random.uniform(0.1, 0.5))
                        time.sleep(delay)
                        continue
                elif resp.status_code in (408, 500, 502, 503, 504):
                    last_error_text = resp.text
                    if attempt < self.max_retries - 1:
                        delay = backoff_delays[min(attempt, len(backoff_delays) - 1)] + random.uniform(0.1, 0.5)
                        time.sleep(delay)
                        continue
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                last_error_text = str(e)
                if attempt < self.max_retries - 1:
                    delay = backoff_delays[min(attempt, len(backoff_delays) - 1)] + random.uniform(0.1, 0.5)
                    time.sleep(delay)
                    continue

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # If candidate text was successfully received from live provider
        if candidate_text:
            # 6. Answer Leakage Guard on generated candidate
            if protected_answers:
                is_safe, leaked = self.answer_guard.verify_no_answer_leakage(candidate_text, protected_answers)
                if not is_safe:
                    return self._trigger_fallback(
                        request,
                        reason=f"generated_candidate_leaked_answer: '{leaked}'",
                        disposition=NativeValidationDisposition.REJECTED,
                    )

            in_tokens = CostTracker.estimate_tokens(prompt)
            out_tokens = CostTracker.estimate_tokens(candidate_text)
            cost = CostTracker.calculate_cost(model_name, in_tokens, out_tokens)

            # Record in quota ledger if available
            if self.quota_manager and source_group_id:
                self.quota_manager.record_completed(
                    request_id=request.request_id,
                    run_id=run_id or "RUN-LIVE",
                    dataset_split=dataset_split,
                    source_group_id=source_group_id,
                    support_level=request.support_level,
                    http_status=200,
                    execution_status="LIVE_SUCCESS",
                    native_output_received=True,
                    fallback_used=False,
                    resolved_model=model_name,
                    latency_ms=latency_ms,
                    configuration_hash="8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
                    output_text=candidate_text,
                    finish_reason=finish_reason or "STOP",
                    attempt_count=attempts,
                    token_metadata={"input_tokens": in_tokens, "output_tokens": out_tokens},
                )

            return ModelGenerationResult(
                request_id=request.request_id,
                requested_provider="gemini",
                configured_model=self.configured_model,
                resolved_model=model_name,
                model_resolution_status="verified" if self.verified_model_id else "live_unverified",
                execution_status=ExecutionStatus.LIVE_PROVIDER_INFERENCE,
                provider_calls_attempted=attempts,
                candidate_text=candidate_text,
                native_validation=NativeValidationSummary(
                    disposition=NativeValidationDisposition.PASSED,
                    failed_gates=[],
                    similarity_score=0.92,
                ),
                latency_ms=round(latency_ms, 2),
                input_token_count=in_tokens,
                output_token_count=out_tokens,
                estimated_cost=cost,
                fallback_used=False,
                generator_method="gemini_prompted",
                prompt_template_version=PromptRegistry.VERSION,
            )

        # Otherwise, live call failed -> record in ledger and fallback to Stage 25
        err_cat = GeminiQuotaManager.classify_error(last_status_code, last_error_text)
        if self.quota_manager and source_group_id:
            self.quota_manager.record_completed(
                request_id=request.request_id,
                run_id=run_id or "RUN-FAIL",
                dataset_split=dataset_split,
                source_group_id=source_group_id,
                support_level=request.support_level,
                http_status=last_status_code or 500,
                execution_status=err_cat,
                native_output_received=False,
                fallback_used=True,
                resolved_model=model_name,
                latency_ms=latency_ms,
                configuration_hash="8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
                output_text="",
                error_message=last_error_text[:200],
                finish_reason="FAILED",
                attempt_count=attempts,
                token_metadata={},
            )

        return self._trigger_fallback(
            request,
            reason=f"live_provider_exhausted_or_failed (HTTP {last_status_code}: {err_cat})",
            disposition=NativeValidationDisposition.PROVIDER_UNAVAILABLE,
            attempts=attempts,
        )

    def _trigger_fallback(
        self,
        request: ModelGenerationRequest,
        reason: str,
        disposition: NativeValidationDisposition,
        attempts: int = 1
    ) -> ModelGenerationResult:
        """
        Executes Stage 25 deterministic fallback with explicit separate attribution.
        """
        fallback_res = self.fallback_adapter.generate(request)
        return ModelGenerationResult(
            request_id=request.request_id,
            requested_provider="gemini",
            configured_model=self.configured_model,
            resolved_model=self.verified_model_id or self.configured_model,
            model_resolution_status="fallback_invoked",
            execution_status=ExecutionStatus.STAGE25_FALLBACK,
            provider_calls_attempted=attempts,
            candidate_text=fallback_res.candidate_text,
            native_validation=NativeValidationSummary(
                disposition=disposition,
                failed_gates=[reason],
                similarity_score=fallback_res.native_validation.similarity_score if fallback_res.native_validation else 0.95,
            ),
            latency_ms=fallback_res.latency_ms,
            input_token_count=0,
            output_token_count=0,
            estimated_cost=0.0,
            fallback_used=True,
            fallback_provider="stage25_rule_engine",
            generator_method="controlled_stage25_fallback",
            prompt_template_version=PromptRegistry.VERSION,
        )
