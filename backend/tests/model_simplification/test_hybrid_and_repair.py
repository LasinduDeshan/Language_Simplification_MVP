"""
Tests for Stage 26 Hybrid Validation Pipeline and Controlled Surface Repair.
"""
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElementsDTO,
    NativeValidationDisposition,
)
from app.model_simplification.hybrid_pipeline import HybridValidationPipeline


def test_controlled_surface_repair():
    pipeline = HybridValidationPipeline()
    raw_output = '```text\nHere is the simplified sentence: "  Put the ball inside the box.  " \n```'
    repaired, ops = pipeline.clean_surface_formatting(raw_output)
    assert repaired == "Put the ball inside the box."
    assert "strip_markdown_codeblock" in ops
    assert "strip_conversational_filler" in ops
    assert "strip_enclosing_quotes" in ops
    assert "normalize_whitespace" in ops


def test_hybrid_validation_passed_candidate():
    pipeline = HybridValidationPipeline()
    req = ModelGenerationRequest(
        request_id="REQ-VAL-01",
        text="Put the red apple into the wooden basket.",
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["red", "apple", "basket"],
        ),
    )
    candidate = "Put the red apple in the basket."
    disp, failed_gates, repairs, final_text, sim = pipeline.validate_candidate(req, candidate)
    assert disp in {NativeValidationDisposition.PASSED, NativeValidationDisposition.PASSED_WITH_CONTROLLED_REPAIR}
    assert len(failed_gates) == 0
    assert "red" in final_text
    assert "apple" in final_text


def test_hybrid_validation_missing_protected_entity_routes_to_manual_review():
    pipeline = HybridValidationPipeline()
    req = ModelGenerationRequest(
        request_id="REQ-VAL-02",
        text="Put the red apple into the wooden basket.",
        support_level="moderate",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["red", "apple", "basket"],
        ),
    )
    # Model dropped "red" and "apple", said "fruit"
    candidate = "Put the fruit in the basket."
    disp, failed_gates, repairs, final_text, sim = pipeline.validate_candidate(req, candidate)
    assert disp == NativeValidationDisposition.MANUAL_REVIEW_REQUIRED
    assert any("missing_protected_term" in g for g in failed_gates)


def test_hybrid_validation_negation_inversion_rejected():
    pipeline = HybridValidationPipeline()
    req = ModelGenerationRequest(
        request_id="REQ-VAL-03",
        text="Do not touch the hot plate.",
        support_level="strong",
    )
    # Model dropped the negation!
    candidate = "Touch the hot plate."
    disp, failed_gates, repairs, final_text, sim = pipeline.validate_candidate(req, candidate)
    assert disp == NativeValidationDisposition.REJECTED
    assert "negation_inversion_detected" in failed_gates
