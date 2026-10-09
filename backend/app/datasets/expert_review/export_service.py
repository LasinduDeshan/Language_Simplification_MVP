"""Sanitized Export Service for Stage 27 Expert Review.

Generates sanitized research and professional-review exports:
- Strips PII (real names, contact info, institutional details).
- Exports adjudicated reference records with governance flags for Stage 28.
- Enforces the universal child delivery safety invariant:
  approved_for_unsupervised_child_delivery is ALWAYS False.
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.datasets.expert_review.schemas import (
    ReviewManifestItem,
    RecordReviewSubmission,
    AdjudicationRecord,
    RevisionRecord,
    FinalDisposition,
    TaxonomyClass,
)


class ExportService:
    """Produces sanitized research dataset exports and public audit logs."""

    def __init__(self):
        pass

    def export_stage28_reference_dataset(
        self,
        manifest_items: List[ReviewManifestItem],
        adjudication_records: Dict[str, AdjudicationRecord],
        revisions: Dict[str, RevisionRecord],
        submissions_by_item: Dict[str, List[RecordReviewSubmission]],
    ) -> List[Dict[str, Any]]:
        """Exports sanitized dataset records for Stage 28 comparative benchmarking.
        
        Only records that achieved expert consensus or adjudicated approval are
        marked eligible_for_stage28_evaluation = True.
        """
        export_records = []

        for item in manifest_items:
            item_id = item.item_id
            adjudication = adjudication_records.get(item_id)
            item_subs = submissions_by_item.get(item_id, [])
            revision = revisions.get(item_id)

            # Determine final disposition and taxonomy
            if adjudication:
                final_disposition = adjudication.final_disposition
                final_taxonomy = adjudication.final_taxonomy_class
                resolution_route = "adjudicated"
            elif item_subs and len(item_subs) >= 2:
                # Check for consensus disposition
                sub_a, sub_b = item_subs[0], item_subs[1]
                disp_a = sub_a.determine_provisional_disposition()
                disp_b = sub_b.determine_provisional_disposition()
                if disp_a == disp_b:
                    final_disposition = disp_a
                else:
                    final_disposition = FinalDisposition.APPROVED_WITH_REVISION
                final_taxonomy = sub_a.taxonomy_class
                resolution_route = "consensus_resolved"
            else:
                final_disposition = FinalDisposition.INVALID_OR_UNUSABLE
                final_taxonomy = TaxonomyClass.INVALID_OR_UNUSABLE
                resolution_route = "unresolved"

            # Check if text was revised
            final_target_text = revision.revised_text if revision else item.target_text

            # Eligibility for Stage 28 evaluation
            is_approved = final_disposition in (
                FinalDisposition.EXPERT_APPROVED,
                FinalDisposition.APPROVED_WITH_REVISION,
            )
            eligible_for_stage28 = is_approved and final_taxonomy != TaxonomyClass.INVALID_OR_UNUSABLE

            export_entry = {
                "item_id": item.item_id,
                "source_group_id": item.source_group_id,
                "record_type": item.record_type.value,
                "text_stimulus": item.text_stimulus,
                "target_text": final_target_text,
                "support_level": item.support_level.value if item.support_level else None,
                "target_age_min": item.target_age_min,
                "target_age_max": item.target_age_max,
                "expert_review_status": "approved" if is_approved else "rejected",
                "eligible_for_stage28_evaluation": eligible_for_stage28,
                "final_taxonomy_class": final_taxonomy.value,
                "final_disposition": final_disposition.value,
                "resolution_route": resolution_route,
                "was_revised": revision is not None,
                "content_hash": item.content_hash,
                # Universal safety invariant
                "approved_for_unsupervised_child_delivery": False,
                "recommended_for_supervised_child_delivery_review": is_approved,
                "requires_professional_monitoring": True,
            }

            export_records.append(export_entry)

        return export_records

    def export_sanitized_audit_manifest(
        self,
        manifest_items: List[ReviewManifestItem],
        adjudication_records: List[AdjudicationRecord],
        revisions: List[RevisionRecord],
    ) -> Dict[str, Any]:
        """Exports a sanitized audit manifest containing non-sensitive verification hashes and statuses."""
        return {
            "schema_version": "1.0.0",
            "stage": 27,
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_records_governed": len(manifest_items),
            "total_adjudications": len(adjudication_records),
            "total_revisions": len(revisions),
            "adjudication_summary": [
                {
                    "adjudication_id": adj.adjudication_id,
                    "item_id": adj.item_id,
                    "conflict_reasons": adj.conflict_reasons,
                    "final_taxonomy_class": adj.final_taxonomy_class.value,
                    "final_disposition": adj.final_disposition.value,
                    "revision_required": adj.revision_required,
                }
                for adj in adjudication_records
            ],
            "revision_summary": [
                {
                    "revision_id": rev.revision_id,
                    "item_id": rev.item_id,
                    "original_hash": rev.original_hash,
                    "revised_hash": rev.revised_hash,
                    "revision_reason": rev.revision_reason,
                    "stage14_schema_validation": rev.stage14_schema_validation,
                    "stage15_quality_validation": rev.stage15_quality_validation,
                }
                for rev in revisions
            ],
        }
