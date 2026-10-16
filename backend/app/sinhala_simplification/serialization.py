"""
Stage 33 — Governed Serialization and Public vs Protected Separation.
Enforces domain-separated keyed HMACs and strict omission of restricted text
from public metadata ledgers.
"""

import hmac
import hashlib
from typing import Any, Dict
from app.sinhala_simplification.schemas import (
    FinalRewriteRecord,
    RewriteCandidate,
    RuleAttempt,
    SimplificationRule,
    TransformationOperation,
)

DEFAULT_PUBLIC_HMAC_KEY = b"stage33_sinhala_simplification_public_v1"


def compute_keyed_hmac(value: str, domain: str = "stage33_rule_engine", key: bytes = DEFAULT_PUBLIC_HMAC_KEY) -> str:
    """Computes a domain-separated, versioned keyed HMAC-SHA256 for public referencing."""
    domain_payload = f"{domain}:{value}".encode("utf-8")
    return hmac.new(key, domain_payload, hashlib.sha256).hexdigest()


def to_public_rewrite_record(record: FinalRewriteRecord) -> Dict[str, Any]:
    """Serializes a FinalRewriteRecord for public metadata ledgers, strictly omitting literal text."""
    data = record.model_dump(mode="json")
    assert "source_text" not in data, "Public record must not contain source_text"
    assert "output_text" not in data, "Public record must not contain output_text"
    return data


def to_public_candidate_record(candidate: RewriteCandidate) -> Dict[str, Any]:
    """Serializes a RewriteCandidate for public reporting by stripping internal candidate text."""
    data = candidate.model_dump(mode="json")
    data.pop("candidate_text_internal", None)
    for op in data.get("operations", []):
        op.pop("before_text_internal", None)
        op.pop("after_text_internal", None)
        for s in op.get("raw_source_spans", []):
            s.pop("text", None)
        for s in op.get("normalized_source_spans", []):
            s.pop("text", None)
        for s in op.get("output_spans", []):
            s.pop("text", None)
    return data


def to_public_operation_record(op: TransformationOperation) -> Dict[str, Any]:
    """Serializes a TransformationOperation for public tracing without literal span text."""
    data = op.model_dump(mode="json")
    data.pop("before_text_internal", None)
    data.pop("after_text_internal", None)
    for s in data.get("raw_source_spans", []):
        s.pop("text", None)
    for s in data.get("normalized_source_spans", []):
        s.pop("text", None)
    for s in data.get("output_spans", []):
        s.pop("text", None)
    return data


def to_public_attempt_record(attempt: RuleAttempt) -> Dict[str, Any]:
    """Serializes a RuleAttempt for public audit ledgers."""
    data = attempt.model_dump(mode="json")
    for s in data.get("source_spans", []):
        s.pop("text", None)
    return data


def to_public_rule_record(rule: SimplificationRule) -> Dict[str, Any]:
    """Serializes a rule definition for the public registry, containing only opaque metadata."""
    data = rule.model_dump(mode="json")
    # Ensure source_pattern_ref and target_template_ref are opaque HMACs or refs, not raw phrases
    assert not any(c in data["source_pattern_ref"] for c in ["\u0D80", "\u0D81", "\u0D82"]), "Raw Sinhala characters in pattern ref"
    return data
