"""
Unit tests for Stage 26 Common Adapter Protocol and Data Contracts.
"""
import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ModelGenerationResult,
    ExecutionStatus,
    NativeValidationDisposition,
    NativeValidationSummary,
    ProtectedElementsDTO,
)
from app.model_simplification.evaluation_schemas import ModelEvaluationResult
from app.model_simplification.adapter import SimplificationModelAdapter


class MockValidAdapter:
    def generate(self, request: ModelGenerationRequest) -> ModelGenerationResult:
        return ModelGenerationResult(
            request_id=request.request_id,
            requested_provider="mock",
            configured_model="mock-v1",
            resolved_model="mock-v1-verified",
            model_resolution_status="verified",
            execution_status=ExecutionStatus.OFFLINE_FIXTURE,
            candidate_text=request.text.lower(),
            native_validation=NativeValidationSummary(
                disposition=NativeValidationDisposition.PASSED,
                failed_gates=[],
                similarity_score=0.95,
            ),
            latency_ms=12.5,
            generator_method="mock_rule",
        )


def test_adapter_protocol_conformance():
    adapter = MockValidAdapter()
    assert isinstance(adapter, SimplificationModelAdapter)

    req = ModelGenerationRequest(
        request_id="GENREQ-001",
        text="Put the big blue ball inside the box.",
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(exact_preservation=["ball", "box"]),
    )
    res = adapter.generate(req)

    assert res.request_id == "GENREQ-001"
    assert res.execution_status == ExecutionStatus.OFFLINE_FIXTURE
    assert res.candidate_text == "put the big blue ball inside the box."
    assert res.native_validation.disposition == NativeValidationDisposition.PASSED


def test_runtime_and_evaluation_dto_separation():
    # Verify runtime DTO does not contain batch-level SARI/BLEU
    res = ModelGenerationResult(
        request_id="GENREQ-002",
        requested_provider="gemini",
        configured_model="${GEMINI_MODEL_ID}",
        resolved_model="gemini-1.5-flash-002",
        model_resolution_status="verified",
        execution_status=ExecutionStatus.LIVE_PROVIDER_INFERENCE,
        candidate_text="Put the blue ball in the box.",
        latency_ms=1450.0,
        generator_method="gemini_prompted",
    )
    assert not hasattr(res, "sari_score")
    assert not hasattr(res, "bleu_score")

    # Verify batch evaluation DTO holds aggregate corpus metrics
    eval_res = ModelEvaluationResult(
        model_id="gemini-1.5-flash-prompted",
        provider="google",
        model_mode="pretrained_prefix_prompt",
        split="validation",
        total_samples=42,
        sari_score=48.5,
        sari_add=35.2,
        sari_keep=65.1,
        sari_del=45.0,
        bleu_score=62.4,
        fkgl_delta=-2.4,
        exact_protected_recall=1.0,
        meaning_preservation_rate=0.98,
        pass_rate=0.88,
        repair_rate=0.07,
        manual_review_rate=0.03,
        rejection_rate=0.02,
        fallback_rate=0.05,
        mean_latency_ms=1520.0,
        p95_latency_ms=2100.0,
        provider_calls_attempted=42,
        provider_outputs_received=42,
        timeout_rate=0.0,
        retry_rate=0.02,
        total_cost=0.00088,
        evaluated_at="2026-10-06T20:00:00Z",
    )
    assert eval_res.sari_score == 48.5
    assert eval_res.total_samples == 42
