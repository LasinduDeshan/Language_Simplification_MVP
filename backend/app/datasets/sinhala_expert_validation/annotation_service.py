"""
Stage 34 — Annotation Submission Service
Validates and records independent blinded expert annotations.
Enforces that submissions cannot contain MISSING in mandatory dimensions and
stores immutable original records.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .audit import AuditLogger
from .enums import AssignmentStatus, DimensionStatus
from .protected_storage import ProtectedStorageManager
from .schemas import AnnotationRecord


class AnnotationService:
    def __init__(
        self,
        storage: Optional[ProtectedStorageManager] = None,
        audit: Optional[AuditLogger] = None,
    ):
        self.storage = storage or ProtectedStorageManager()
        self.audit = audit or AuditLogger(self.storage)
        self._annotations: Dict[str, AnnotationRecord] = {}

    def submit_annotation(self, record: AnnotationRecord) -> AnnotationRecord:
        # Validate that record is marked as submitted and has no MISSING
        record.is_draft = False
        record.validate_submission_completeness()

        if record.annotation_id in self._annotations:
            raise ValueError(
                f"Immutable violation: Annotation {record.annotation_id} has already been submitted and cannot be overwritten."
            )

        self._annotations[record.annotation_id] = record

        # Store immutable copy in protected storage
        self.storage.store_json(
            "annotations",
            f"{record.annotation_id}.json",
            record.model_dump(),
        )

        # Audit log the submission
        self.audit.log_event(
            actor_id=record.reviewer_id,
            action="ANNOTATION_SUBMITTED",
            object_id=record.annotation_id,
            outcome="SUCCESS",
            rule_or_version=record.rubric_version,
            details={
                "item_id": record.item_id,
                "overall_disposition": record.overall_disposition.score,
                "confidence": record.confidence,
            },
        )

        return record

    def get_annotation(self, annotation_id: str) -> Optional[AnnotationRecord]:
        return self._annotations.get(annotation_id)

    def list_annotations_for_item(self, item_id: str) -> List[AnnotationRecord]:
        return [ann for ann in self._annotations.values() if ann.item_id == item_id]

    def to_sanitized_records(self) -> List[Dict[str, Any]]:
        """Returns repository-safe representation excluding raw comments or protected text."""
        records = []
        for ann in self._annotations.values():
            d = ann.model_dump()
            d.pop("protected_comment_ref", None)
            d["has_protected_comments"] = ann.has_protected_comments
            records.append(d)
        return records
