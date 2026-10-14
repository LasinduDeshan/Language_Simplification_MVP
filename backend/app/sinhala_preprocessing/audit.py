"""
Privacy-safe audit logging for Stage 30 Sinhala Preprocessing.
Ensures that log records contain only record identifiers, SHA-256 hashes,
operation counts, rule codes, and terminal dispositions.
Never writes raw or normalized child/learner text to log sinks.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger("sinhala_preprocessing_audit")

def log_audit_event(
    record_id: str,
    raw_sha256: str,
    normalized_sha256: str,
    final_disposition: str,
    disposition_reason_code: str = None,
    quality_flags: list = None,
    operation_count: int = 0,
    sentence_count: int = 0,
    token_count: int = 0,
    grapheme_count: int = 0
) -> Dict[str, Any]:
    """
    Produce and emit a privacy-safe structured audit event.
    """
    event = {
        "event_type": "SINHALA_PREPROCESSING_DISPOSITION",
        "record_id": record_id,
        "raw_sha256": raw_sha256,
        "normalized_sha256": normalized_sha256,
        "final_disposition": final_disposition,
        "disposition_reason_code": disposition_reason_code,
        "quality_flags": quality_flags or [],
        "operation_count": operation_count,
        "sentence_count": sentence_count,
        "token_count": token_count,
        "grapheme_count": grapheme_count,
        "approved_for_child_delivery": False
    }
    logger.info("AUDIT_DISPOSITION: %s", event)
    return event
