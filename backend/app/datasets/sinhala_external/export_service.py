"""
Export Filtering and Rights Enforcement Service for Stage 31 Pilot Corpus.
Enforces non-redistribution constraints:
- SRC-SI-004 (UCSC LTRL): PROTECTED_INTERNAL_ONLY -> literal text 100% suppressed
- SRC-SI-002 (AI4Bharat IndicCorp): REVIEW_REQUIRED_ARTIFACT_LICENCE_MISMATCH -> literal text 100% suppressed
  pending artifact-specific licence verification (CC0 vs CC BY-NC-SA 4.0 ambiguity)
Preserves canonical analytical view fields and reproducible keyed HMAC metadata.
"""

from typing import Any, Dict, Optional
from app.datasets.sinhala_external.schemas import PilotCorpusRecord

def build_public_export_record(record: PilotCorpusRecord, text: str) -> Optional[Dict[str, Any]]:
    """Transforms a PilotCorpusRecord into a public export record enforcing licensing constraints."""
    if record.effective_export_policy in ["BLOCKED_PROPRIETARY", "BLOCKED_REVIEW_REQUIRED", "METADATA_CATALOGUE_ONLY"]:
        return None

    is_protected_internal = (
        record.effective_export_policy == "PROTECTED_INTERNAL_ONLY" or
        not record.literal_text_redistributable or
        "SRC-SI-004" in record.all_contributing_sources or
        record.source_id == "SRC-SI-004"
    )

    is_licence_mismatch = (
        record.source_id == "SRC-SI-002" or
        "SRC-SI-002" in record.all_contributing_sources
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
        "canonical_record_id": record.canonical_record_id,
        "is_canonical_exact_record": record.is_canonical_exact_record,
        "exact_duplicate_weight": record.exact_duplicate_weight,
        "retention_reason": record.retention_reason,
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
    elif is_licence_mismatch:
        # Literal text suppressed pending artifact-specific licence verification
        export_dict["text"] = None
        export_dict["export_redistribution_status"] = "REVIEW_REQUIRED_ARTIFACT_LICENCE_MISMATCH"
    else:
        export_dict["text"] = text
        export_dict["export_redistribution_status"] = "PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION"

    return export_dict
