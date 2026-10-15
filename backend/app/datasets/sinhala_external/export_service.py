"""
Export Filtering and Rights Enforcement Service for Stage 31 Pilot Corpus.
Enforces non-redistribution constraints (e.g. SRC-SI-004 PROTECTED_INTERNAL_ONLY),
suppressing literal text for restricted sources while preserving reproducible metadata.
"""

from typing import Any, Dict, Optional
from app.datasets.sinhala_external.schemas import PilotCorpusRecord

def build_public_export_record(record: PilotCorpusRecord, text: str) -> Optional[Dict[str, Any]]:
    """Transforms a PilotCorpusRecord into a public export record enforcing licensing constraints."""
    if record.effective_export_policy in ["BLOCKED_PROPRIETARY", "BLOCKED_REVIEW_REQUIRED", "METADATA_CATALOGUE_ONLY"]:
        return None

    is_protected_internal = (
        record.effective_export_policy == "PROTECTED_INTERNAL_ONLY" or
        not record.literal_text_redistributable
    )

    export_dict: Dict[str, Any] = {
        "record_id": record.record_id,
        "split": record.split.value,
        "split_group_id": record.split_group_id,
        "component_type": record.component_type.value,
        "primary_source_id": record.source_id,
        "all_contributing_sources": record.all_contributing_sources,
        "public_record_digest": record.public_record_digest,
        "hmac_key_id": record.hmac_key_id,
        "provisional_domain": record.provisional_domain,
        "sentence_count": record.sentence_count,
        "token_count": record.token_count,
        "grapheme_count": record.grapheme_count,
        "effective_export_policy": record.effective_export_policy,
        "literal_text_redistributable": record.literal_text_redistributable,
        "governance_status": {
            "validation_status": "draft",
            "research_eligible": False,
            "approved_for_child_delivery": False,
            "requires_expert_review": True
        }
    }

    if is_protected_internal:
        # Literal text suppressed in compliance with Academic Research Agreement
        export_dict["text"] = None
        export_dict["export_redistribution_status"] = "LITERAL_TEXT_SUPPRESSED_PROTECTED_INTERNAL_ONLY"
    else:
        export_dict["text"] = text
        export_dict["export_redistribution_status"] = "PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION"

    return export_dict
