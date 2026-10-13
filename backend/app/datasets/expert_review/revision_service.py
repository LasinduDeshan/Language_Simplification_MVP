"""Revision Service for Stage 27 Expert Review.

Manages versioned text revisions, provenance preservation, parent-child record linkage,
and revalidation hooks integrating Stage 14 schema validation and Stage 15 automated quality checks.
"""
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.datasets.expert_review.schemas import (
    RevisionRecord,
    FinalDisposition,
    ReviewRecordType,
)
from app.datasets.quality.registry import QualityValidatorRegistry
from app.datasets.quality.enums import RuleSeverity


class RevisionService:
    """Coordinates versioned text revisions and executes Stage 14/15 quality validation hooks."""

    def __init__(self):
        self.revisions: Dict[str, RevisionRecord] = {}
        self.item_revisions: Dict[str, List[str]] = {}
        self.quality_registry = QualityValidatorRegistry()

    def create_revision(
        self,
        item_id: str,
        original_text: str,
        revised_text: str,
        source_group_id: str,
        revision_reason: str,
        revised_by: str,
        record_type: ReviewRecordType = ReviewRecordType.SIMPLIFICATION_PAIR,
        is_material_revision: bool = False,
        support_level: str = "moderate",
        target_age_min: int = 4,
        target_age_max: int = 8,
    ) -> RevisionRecord:
        """Creates a provenance-preserving revision and executes Stage 14 and Stage 15 validation hooks."""
        if not revised_text or not revised_text.strip():
            raise ValueError("revised_text cannot be empty.")

        # Compute deterministic content hashes
        original_hash = hashlib.sha256(original_text.strip().encode("utf-8")).hexdigest()
        revised_hash = hashlib.sha256(revised_text.strip().encode("utf-8")).hexdigest()

        revision_id = f"REV-{uuid.uuid4().hex[:8]}"

        # Hook 1: Stage 14 Schema Validation
        stage14_status = self._run_stage14_validation(
            item_id=item_id,
            revised_text=revised_text,
            record_type=record_type,
            target_age_min=target_age_min,
            target_age_max=target_age_max,
        )

        # Hook 2: Stage 15 Automated Quality Validation
        stage15_status = self._run_stage15_validation(
            item_id=item_id,
            original_text=original_text,
            revised_text=revised_text,
            record_type=record_type,
            support_level=support_level,
        )

        # Determine disposition based on validation checks
        if stage14_status == "PASSED" and stage15_status == "PASSED":
            disposition = FinalDisposition.APPROVED_WITH_REVISION
        else:
            disposition = FinalDisposition.INVALID_OR_UNUSABLE

        record = RevisionRecord(
            revision_id=revision_id,
            item_id=item_id,
            source_group_id=source_group_id,
            original_text=original_text,
            revised_text=revised_text,
            original_hash=original_hash,
            revised_hash=revised_hash,
            revision_reason=revision_reason,
            revised_by=revised_by,
            stage14_schema_validation=stage14_status,
            stage15_quality_validation=stage15_status,
            final_disposition=disposition,
            created_at=datetime.utcnow(),
        )

        self.revisions[revision_id] = record
        if item_id not in self.item_revisions:
            self.item_revisions[item_id] = []
        self.item_revisions[item_id].append(revision_id)

        return record

    def _run_stage14_validation(
        self,
        item_id: str,
        revised_text: str,
        record_type: ReviewRecordType,
        target_age_min: int,
        target_age_max: int,
    ) -> str:
        """Executes Stage 14 schema structural validations."""
        try:
            if not item_id or not isinstance(item_id, str):
                return "FAILED: Missing or invalid item_id"
            if target_age_min > target_age_max:
                return f"FAILED: target_age_min ({target_age_min}) exceeds target_age_max ({target_age_max})"
            if target_age_min < 4 or target_age_max > 8:
                return f"FAILED: Target age range ({target_age_min}-{target_age_max}) outside supported 4-8 range"
            if len(revised_text.strip()) == 0:
                return "FAILED: Empty revised text"
            return "PASSED"
        except Exception as exc:
            return f"FAILED: Schema validation exception: {str(exc)}"

    def _run_stage15_validation(
        self,
        item_id: str,
        original_text: str,
        revised_text: str,
        record_type: ReviewRecordType,
        support_level: str,
    ) -> str:
        """Executes Stage 15 quality checks using QualityValidatorRegistry."""
        try:
            # Map review record type to dataset layer
            if record_type == ReviewRecordType.SIMPLIFICATION_PAIR:
                layer = "simplification_corpus"
                p_id = item_id if (item_id.startswith("SIMP-") and len(item_id.split("-")) == 3) else "SIMP-EN-000001"
                mock_record = {
                    "schema_version": "1.0.0",
                    "pair_id": p_id,
                    "original_text": original_text,
                    "simplified_text": revised_text,
                    "support_level": support_level,
                    "language": "en",
                    "age_min": 4,
                    "age_max": 8,
                }
            elif record_type == ReviewRecordType.LEXICON_ENTRY:
                layer = "lexicons"
                e_id = item_id if (item_id.startswith("LEX-") and len(item_id.split("-")) == 3) else "LEX-EN-000001"
                mock_record = {
                    "schema_version": "1.0.0",
                    "entry_id": e_id,
                    "language": "en",
                    "headword": revised_text.split()[0] if revised_text else "word",
                    "suggested_replacements": [revised_text],
                    "target_age_min": 4,
                    "target_age_max": 8,
                    "child_friendly_definition": revised_text,
                }
            else:
                layer = "adaptation_test_set"
                a_id = item_id if (item_id.startswith("ADAPT-") and len(item_id.split("-")) == 3) else "ADAPT-EN-000001"
                mock_record = {
                    "schema_version": "1.0.0",
                    "activity_id": a_id,
                    "language": "en",
                    "prompt": revised_text,
                    "target_age_min": 4,
                    "target_age_max": 8,
                }

            # Run validators from registry
            rule_results = self.quality_registry.validate_record(
                record=mock_record,
                dataset_layer=layer,
                run_id=f"REV-VAL-{uuid.uuid4().hex[:6]}",
                enable_nlp=False,  # deterministic fast execution for revision hook
            )

            # Check for critical or error level failures
            failures = [
                r.message for r in rule_results
                if not r.passed and r.severity in (RuleSeverity.ERROR, RuleSeverity.CRITICAL)
            ]

            if failures:
                return f"FAILED: {'; '.join(failures[:3])}"
            return "PASSED"
        except Exception as exc:
            return f"FAILED: Quality validation exception: {str(exc)}"

    def get_revision(self, revision_id: str) -> Optional[RevisionRecord]:
        return self.revisions.get(revision_id)

    def get_revisions_for_item(self, item_id: str) -> List[RevisionRecord]:
        rev_ids = self.item_revisions.get(item_id, [])
        return [self.revisions[rid] for rid in rev_ids if rid in self.revisions]

    def list_revisions(self) -> List[RevisionRecord]:
        return list(self.revisions.values())

    def get_sanitized_audit_trail(self) -> List[Dict[str, Any]]:
        """Produces a sanitized public audit trail stripping raw text and reviewer PII."""
        trail = []
        for rev in self.revisions.values():
            trail.append({
                "revision_id": rev.revision_id,
                "item_id": rev.item_id,
                "source_group_id": rev.source_group_id,
                "original_hash": rev.original_hash,
                "revised_hash": rev.revised_hash,
                "revision_reason": rev.revision_reason,
                "stage14_schema_validation": rev.stage14_schema_validation,
                "stage15_quality_validation": rev.stage15_quality_validation,
                "final_disposition": rev.final_disposition.value,
                "created_at": rev.created_at.isoformat(),
            })
        return trail
