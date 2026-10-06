"""
End-to-End integration test for Stage 26 Simplification Service.
"""
from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElementsDTO,
)
from app.model_simplification.generation_service import ModelSimplificationService


def test_stage26_service_governance_invariants():
    service = ModelSimplificationService()
    req = ModelGenerationRequest(
        request_id="REQ-E2E-01",
        text="Before you select the red apple, pick the yellow banana.",
        support_level="strong",
        protected_elements=ProtectedElementsDTO(
            exact_preservation=["red", "apple", "yellow", "banana"],
        ),
    )
    res = service.simplify(req, model_id="stage25-controlled-deterministic")
    
    # Check invariant fields
    gov = res["governance"]
    assert gov["validation_status"] == "draft"
    assert gov["research_eligible"] is False
    assert gov["approved_for_child_delivery"] is False
    assert gov["requires_expert_review"] is True
    
    # Check delivery outcome
    assert res["accounting_outcome"] in {"native_delivered", "repair_delivered"}
    assert res["candidate_text"] is not None
    assert len(res["candidate_text"]) > 0
