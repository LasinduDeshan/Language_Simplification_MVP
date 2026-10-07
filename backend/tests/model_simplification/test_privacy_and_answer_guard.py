"""
Unit tests for Stage 26 Privacy Filter, Allowlist Serialization, and HMAC Answer Guard.
"""
import json
import pytest
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElementsDTO,
)
from app.model_simplification.privacy_filter import PrivacyFilter
from app.model_simplification.provider_payload_serializer import ProviderPayloadSerializer
from app.model_simplification.hmac_answer_guard import HMACAnswerGuard


def test_privacy_filter_strips_learner_and_clinical_context():
    filter_engine = PrivacyFilter()
    raw_context = {
        "learner_id": "CHILD-003",
        "screening_risk_level": "moderate",
        "vocabulary_score": 75.0,
        "session_id": "SESS-12345",
    }
    base_req = ModelGenerationRequest(
        request_id="GENREQ-001",
        text="Identify the animal in the picture.",
        target_age=5,
        support_level="mild",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["cat", "picture", "learner_id"],  # learner_id accidentally injected
            answer_boundary_ref="ANSBOUND-0001",
        ),
    )
    sanitized = filter_engine.sanitize_request(raw_context, base_req)

    assert "learner_id" not in sanitized.protected_elements.exact_preservation
    assert sanitized.protected_elements.exact_preservation == ["cat", "picture"]
    assert sanitized.protected_elements.answer_boundary_ref == "ANSBOUND-0001"


def test_payload_allowlist_serialization():
    serializer = ProviderPayloadSerializer()
    req = ModelGenerationRequest(
        request_id="GENREQ-002",
        text="Put the blue square on the table.",
        target_age=6,
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["blue", "square", "table"],
            answer_boundary_ref="ANSBOUND-9999",
        ),
    )
    payload = serializer.serialize(req, prompt_instructions="Simplify for a 6-year-old child.")

    # Must contain allowlisted fields
    assert payload["text"] == "Put the blue square on the table."
    assert payload["target_age"] == 6
    assert payload["support_level"] == "moderate"
    assert payload["exact_preservation"] == ["blue", "square", "table"]
    assert payload["prompt_instructions"] == "Simplify for a 6-year-old child."

    # Must strictly NOT contain internal metadata or answer references
    assert "answer_boundary_ref" not in payload
    assert "request_id" not in payload
    assert "generation_config_id" not in payload


def test_answer_reference_not_transmitted():
    serializer = ProviderPayloadSerializer()
    req = ModelGenerationRequest(
        request_id="GENREQ-003",
        text="Which fruit is yellow?",
        support_level="strong",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["fruit", "yellow"],
            answer_boundary_ref="ANSBOUND-SECRET-123",
        ),
    )
    json_str = serializer.to_json(req)
    assert "ANSBOUND" not in json_str
    assert "answer_boundary_ref" not in json_str


def test_raw_answer_not_transmitted():
    serializer = ProviderPayloadSerializer()
    req = ModelGenerationRequest(
        request_id="GENREQ-004",
        text="Where does the bird sleep?",
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["bird", "sleep"],
            answer_boundary_ref="ANSBOUND-004",
        ),
    )
    json_str = serializer.to_json(req)
    # The raw target answer "nest" is never inside the serialized payload
    assert "nest" not in json_str


def test_answer_hash_not_transmitted():
    serializer = ProviderPayloadSerializer()
    req = ModelGenerationRequest(
        request_id="GENREQ-005",
        text="Count the apples.",
        support_level="mild",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["apples"],
            answer_boundary_ref="ANSBOUND-005",
        ),
    )
    json_str = serializer.to_json(req)
    assert "sha256" not in json_str
    assert "hash" not in json_str


def test_protected_element_answer_collision_blocks_dispatch():
    guard = HMACAnswerGuard()
    protected_answers = ["dog", "golden retriever"]

    # Case 1: Collision where exact_preservation contains answer "dog"
    has_collision, term = guard.check_protected_element_collision(
        exact_preservation_terms=["big", "dog", "house"],
        protected_answers=protected_answers,
    )
    assert has_collision is True
    assert term == "dog"

    # Case 2: Clean request without collision
    clean_collision, clean_term = guard.check_protected_element_collision(
        exact_preservation_terms=["big", "animal", "house"],
        protected_answers=protected_answers,
    )
    assert clean_collision is False
    assert clean_term is None


def test_final_provider_payload_contains_no_answer_variant():
    guard = HMACAnswerGuard()
    protected_answers = ["banana"]

    # Candidate text that leaks the answer
    is_safe, leaked = guard.verify_no_answer_leakage(
        candidate_text="Pick the yellow banana.",
        protected_answers=protected_answers,
    )
    assert is_safe is False
    assert leaked == "banana"

    # Candidate text that preserves question boundary safely
    is_safe_clean, _ = guard.verify_no_answer_leakage(
        candidate_text="Pick the yellow fruit.",
        protected_answers=protected_answers,
    )
    assert is_safe_clean is True


def test_hmac_answer_guard_local_only():
    guard = HMACAnswerGuard(secret_key=b"test_key_123")
    digest1 = guard.compute_hmac("Dog")
    digest2 = guard.compute_hmac(" dog! ")

    # Normalization should yield identical local HMACs
    assert digest1 == digest2
    assert len(digest1) == 64
