"""
Stage 26 Provider Payload Serializer.
Enforces strict allowlist-only serialization for external LLM API payloads (e.g. Gemini).
Guarantees that answer_boundary_ref, raw answers, hashes, learner IDs, screening risks,
or private scores never leave the local backend boundary.
"""
import json
from typing import Dict, Any, List
from app.model_simplification.schemas import ModelGenerationRequest


class ProviderPayloadSerializer:
    """
    Allowlist serializer for external model providers.
    """

    ALLOWLIST_KEYS = {
        "text",
        "language",
        "target_age",
        "support_level",
        "content_type",
        "response_mode",
        "exact_preservation",
        "prompt_instructions",
    }

    FORBIDDEN_KEY_PATTERNS = {
        "answer",
        "boundary",
        "ref",
        "hash",
        "learner",
        "child",
        "risk",
        "score",
        "session",
    }

    def serialize(self, request: ModelGenerationRequest, prompt_instructions: str = "") -> Dict[str, Any]:
        """
        Builds a strictly allowlisted dictionary for external dispatch.
        """
        payload: Dict[str, Any] = {
            "text": request.text,
            "language": request.language,
            "target_age": request.target_age,
            "support_level": request.support_level,
            "content_type": request.content_type,
            "response_mode": request.response_mode,
            "exact_preservation": list(request.protected_elements.exact_preservation),
        }
        if prompt_instructions:
            payload["prompt_instructions"] = prompt_instructions

        # Allowlist filter
        filtered_payload = {k: v for k, v in payload.items() if k in self.ALLOWLIST_KEYS}

        # Double check no internal answer reference or leakage key was added
        for k in filtered_payload.keys():
            if "answer" in k or "boundary" in k or "hash" in k or "ref" in k:
                raise ValueError(f"Security invariant violated: forbidden key '{k}' detected in external payload!")

        return filtered_payload

    def to_json(self, request: ModelGenerationRequest, prompt_instructions: str = "") -> str:
        payload = self.serialize(request, prompt_instructions)
        return json.dumps(payload, ensure_ascii=False)
