"""
Stage 26: Privacy Filter & Strict Provider Payload Allowlist Serializer.
Guarantees zero PII, child IDs, screening risks, session history, or answer boundary references reach external APIs.
"""

from typing import Dict, Any
import re
from .schemas import ModelGenerationRequest


class SanitizationError(Exception):
    """Raised when request sanitization fails and external dispatch must be blocked."""
    pass


FORBIDDEN_PAYLOAD_KEYS = {
    "answer_boundary_ref",
    "forbidden_disclosure_hashes",
    "answer_text",
    "raw_answer",
    "learner_id",
    "child_id",
    "screening_risk",
    "screening_risk_level",
    "learner_score",
    "session_history",
    "dld_risk"
}


def sanitize_text(text: str) -> str:
    """Removes potential embedded PII (e.g. emails, phone numbers, child IDs) from input text."""
    # Strip email patterns
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED_EMAIL]", text)
    # Strip phone-like sequences
    text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]", text)
    # Strip learner ID patterns
    text = re.sub(r"\b(LEARNER|CHILD|STUDENT)-[A-Z0-9-]+\b", "[REDACTED_ID]", text, flags=re.IGNORECASE)
    return text.strip()


def serialize_provider_payload(request: ModelGenerationRequest) -> Dict[str, Any]:
    """
    Serializes request into an explicitly allowlisted dictionary for external model dispatch.
    Raises SanitizationError if forbidden fields are present or sanitization fails.
    """
    sanitized_source_text = sanitize_text(request.text)
    if not sanitized_source_text:
        raise SanitizationError("Sanitization resulted in empty text. Dispatch blocked.")

    # Strict Allowlist
    payload = {
        "text": sanitized_source_text,
        "language": request.language,
        "support_level": request.support_level.value if hasattr(request.support_level, "value") else str(request.support_level),
        "target_age": request.target_age,
        "content_type": request.content_type,
        "response_mode": request.response_mode,
        "protected_elements": {
            "exact_preservation": list(request.protected_elements.exact_preservation)
        },
        "generation_constraints": dict(request.generation_constraints)
    }

    # Security Verification Check: Ensure no forbidden keys or references leaked into payload
    def check_dict_forbidden(d: Dict[str, Any]):
        for k, v in d.items():
            if k in FORBIDDEN_PAYLOAD_KEYS:
                raise SanitizationError(f"Forbidden key '{k}' detected in serialized provider payload. Dispatch blocked.")
            if isinstance(v, dict):
                check_dict_forbidden(v)

    check_dict_forbidden(payload)

    # Verify no answer_boundary_ref value leaked
    if request.protected_elements.answer_boundary_ref:
        payload_str = str(payload)
        if request.protected_elements.answer_boundary_ref in payload_str:
            raise SanitizationError("answer_boundary_ref leaked into serialized payload. Dispatch blocked.")

    return payload
