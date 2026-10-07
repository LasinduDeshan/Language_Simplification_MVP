"""
Privacy-safe audit logging for Stage 25 controlled simplification.
Logs pseudonymous identifiers, SHA-256 hashes, applied rules, and decisions without leaking raw learner text.
"""

import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.controlled_simplification.schemas import SimplificationResponse


logger = logging.getLogger("controlled_simplification_audit")


class PrivacySafeAuditor:
    """
    Produces structured, privacy-safe audit records for governance and compliance.
    """

    @staticmethod
    def create_audit_record(
        response: SimplificationResponse,
        include_raw_text: bool = False
    ) -> Dict[str, Any]:
        """
        Builds a privacy-safe audit dictionary.
        """
        record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": response.request_id,
            "engine_version": response.engine_version,
            "configuration_hash": response.configuration_hash,
            "original_text_hash": response.original_text_hash,
            "simplified_text_hash": hashlib.sha256(response.simplified_text.encode("utf-8")).hexdigest(),
            "requested_support_level": response.requested_support_level.value if response.requested_support_level else None,
            "recommended_support_level": response.recommended_support_level.value if response.recommended_support_level else None,
            "applied_support_level": response.applied_support_level.value,
            "support_level_source": response.support_level_source.value,
            "support_override_reason": response.support_override_reason,
            "terminal_status": response.status.value,
            "applied_rule_ids": [op.rule_id for op in response.applied_operations if op.status == "applied"],
            "validation_passed": response.validation_results.all_critical_passed,
            "detected_violations_count": len(response.validation_results.detected_violations),
            "attempt_number": response.scaffolding_metadata.attempt_number,
            "requires_adult_escalation": response.scaffolding_metadata.requires_adult_escalation
        }

        if include_raw_text:
            record["_research_raw_text"] = {
                "original": response.original_text,
                "simplified": response.simplified_text
            }

        return record

    @classmethod
    def log_response(cls, response: SimplificationResponse, include_raw_text: bool = False) -> Dict[str, Any]:
        """
        Logs and returns the privacy-safe audit record.
        """
        record = cls.create_audit_record(response, include_raw_text=include_raw_text)
        logger.info(f"SIMPLIFICATION_AUDIT: {json.dumps(record)}")
        return record
