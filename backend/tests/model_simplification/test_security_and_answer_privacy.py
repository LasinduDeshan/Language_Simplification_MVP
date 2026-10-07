"""
Tests for Stage 26 Payload Serialization, Answer Guard, Privacy Filtering, and Metric Restrictions.
"""
import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElementsDTO,
    ModelGenerationResult,
    ExecutionStatus,
)
from app.model_simplification.provider_payload_serializer import ProviderPayloadSerializer
from app.model_simplification.privacy_filter import PrivacyFilter
from app.model_simplification.hmac_answer_guard import HMACAnswerGuard


def test_payload_allowlist_serialization():
    serializer = ProviderPayloadSerializer()
    req = ModelGenerationRequest(
        request_id="REQ-001",
        text="Pick the red ball.",
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["red", "ball"],
            answer_boundary_ref="ANS-SECRET-001",
            semantic_equivalence_refs=["SEM-001"],
        ),
    )
    serialized = serializer.serialize(req, prompt_instructions="Simplify clearly.")
    
    # Assert allowlisted fields are present
    assert serialized["text"] == "Pick the red ball."
    assert serialized["support_level"] == "moderate"
    assert serialized["exact_preservation"] == ["red", "ball"]
    assert serialized["prompt_instructions"] == "Simplify clearly."
    
    # Assert answer_boundary_ref and internal keys are completely omitted
    assert "answer_boundary_ref" not in serialized
    assert "semantic_equivalence_refs" not in serialized
    assert "request_id" not in serialized


def test_answer_reference_and_hash_not_transmitted():
    serializer = ProviderPayloadSerializer()
    json_payload = serializer.to_json(
        ModelGenerationRequest(
            request_id="REQ-002",
            text="Touch the square.",
            support_level="mild",
            protected_elements=ProtectedElementsDTO(
                exact_preservation=["square"],
                answer_boundary_ref="ANS-BOUND-999",
            ),
        )
    )
    assert "ANS-BOUND-999" not in json_payload
    assert "answer" not in json_payload.lower()
    assert "hash" not in json_payload.lower()


def test_protected_element_answer_collision_blocks_dispatch():
    guard = HMACAnswerGuard()
    # Case: protected element accidentally includes the target answer "triangle"
    has_collision, colliding_term = guard.check_protected_element_collision(
        exact_preservation_terms=["find", "green", "triangle"],
        protected_answers=["triangle"],
    )
    assert has_collision is True
    assert colliding_term == "triangle"

    # Case: clean terms with no answer overlap
    safe_collision, term = guard.check_protected_element_collision(
        exact_preservation_terms=["find", "green", "shape"],
        protected_answers=["triangle"],
    )
    assert safe_collision is False
    assert term is None


def test_privacy_filter_strips_learner_and_clinical_fields():
    filter_engine = PrivacyFilter()
    req = ModelGenerationRequest(
        request_id="REQ-003",
        text="Put the star in the basket.",
        support_level="strong",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["star", "basket"],
        ),
    )
    raw_context = {
        "learner_id": "CHILD-994",
        "screening_risk_level": "high_risk",
        "comprehension_score": 0.35,
        "session_id": "SESS-1234",
    }
    sanitized = filter_engine.sanitize_request(raw_context, req)
    assert sanitized.text == req.text
    # Ensure no context fields injected
    assert not hasattr(sanitized, "learner_id")
    assert not hasattr(sanitized, "screening_risk_level")


def test_cached_output_metric_restrictions():
    cached_res = ModelGenerationResult(
        request_id="REQ-004",
        requested_provider="gemini",
        configured_model="gemini-1.5-flash",
        resolved_model="gemini-1.5-flash-001",
        execution_status=ExecutionStatus.CACHED_NATIVE_OUTPUT,
        candidate_text="Select the star.",
        latency_ms=0.0,
        generator_method="cached_eval",
        quality_metrics_permitted=True,
        current_latency_metrics_permitted=False,
        current_provider_reliability_metrics_permitted=False,
    )
    assert cached_res.quality_metrics_permitted is True
    assert cached_res.current_latency_metrics_permitted is False
    assert cached_res.current_provider_reliability_metrics_permitted is False
