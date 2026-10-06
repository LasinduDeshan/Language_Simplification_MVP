"""
Stage 26 Privacy Filter.
Sanitizes generation requests to guarantee zero transmission of raw learner IDs,
screening risk labels, educational scores, or private session histories to external providers.
"""
from typing import Dict, Any
from app.model_simplification.schemas import ModelGenerationRequest, ProtectedElementsDTO


class PrivacyFilter:
    """
    Strips private learner and clinical context before model serialization.
    """

    FORBIDDEN_FIELDS = {
        "learner_id",
        "child_id",
        "learner_code",
        "screening_risk_level",
        "risk_support_level",
        "screening_version",
        "screening_source",
        "vocabulary_score",
        "grammar_score",
        "comprehension_score",
        "instruction_following_score",
        "session_id",
        "interaction_history",
        "raw_answers",
        "protected_answer",
        "answer_hashes",
    }

    def sanitize_request(self, raw_context: Dict[str, Any], base_request: ModelGenerationRequest) -> ModelGenerationRequest:
        """
        Ensures the request contains only allowed pedagogical and linguistic context.
        """
        # Verify no forbidden keys leak into protected elements
        clean_exact = [
            term for term in base_request.protected_elements.exact_preservation
            if term.lower() not in self.FORBIDDEN_FIELDS
        ]
        
        sanitized_elements = ProtectedElementsDTO(
            exact_preservation=clean_exact,
            semantic_equivalence_refs=base_request.protected_elements.semantic_equivalence_refs,
            answer_boundary_ref=base_request.protected_elements.answer_boundary_ref,
        )

        return ModelGenerationRequest(
            request_id=base_request.request_id,
            text=base_request.text,
            language=base_request.language,
            target_age=base_request.target_age,
            support_level=base_request.support_level,
            content_type=base_request.content_type,
            response_mode=base_request.response_mode,
            protected_elements=sanitized_elements,
            action_graph_ref=base_request.action_graph_ref,
            generation_config_id=base_request.generation_config_id,
        )
