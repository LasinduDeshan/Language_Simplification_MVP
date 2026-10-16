"""
Stage 34 — Adjudication Service
Identifies items requiring adjudication, manages adjudicator determinations without
overwriting independent annotations, and reconciles Level 6 accounting.
"""

from typing import Any, Dict, List, Optional
from .audit import AuditLogger
from .enums import AdjudicationDisposition, DimensionStatus, OverallDisposition, ReasonCode, SafetyFlag
from .protected_storage import ProtectedStorageManager
from .schemas import AdjudicationRecord, AnnotationRecord


class AdjudicationService:
    def __init__(
        self,
        storage: Optional[ProtectedStorageManager] = None,
        audit: Optional[AuditLogger] = None,
    ):
        self.storage = storage or ProtectedStorageManager()
        self.audit = audit or AuditLogger(self.storage)
        self._queue: Dict[str, Dict[str, Any]] = {}
        self._adjudications: Dict[str, AdjudicationRecord] = {}

    def inspect_item_for_adjudication(
        self,
        item_id: str,
        annotations: List[AnnotationRecord],
    ) -> Optional[Dict[str, Any]]:
        """Determines whether an item requires adjudication under governed rules."""
        if len(annotations) < 2:
            return None

        triggers = []

        # Check safety flags
        for ann in annotations:
            if ann.safety.status == DimensionStatus.RATED and ann.safety.score in [
                SafetyFlag.POTENTIAL_CONCERN.value,
                SafetyFlag.UNSUITABLE.value,
                SafetyFlag.UNCERTAIN.value,
            ]:
                triggers.append(f"SAFETY_CONCERN_{ann.safety.score}")

        # Check reject/escalate dispositions
        for ann in annotations:
            if ann.overall_disposition.status == DimensionStatus.RATED and ann.overall_disposition.score in [
                OverallDisposition.REJECT.value,
                OverallDisposition.ESCALATE.value,
            ]:
                triggers.append(f"DISPOSITION_{ann.overall_disposition.score}")

        # Check major semantic drift (meaning preservation <= 1)
        for ann in annotations:
            if (
                ann.meaning_preservation.status == DimensionStatus.RATED
                and isinstance(ann.meaning_preservation.score, int)
                and ann.meaning_preservation.score <= 1
            ):
                triggers.append("MAJOR_SEMANTIC_DRIFT")

        # Check ordinal span >= 2 points on meaning or grammar
        meaning_scores = [
            ann.meaning_preservation.score
            for ann in annotations
            if ann.meaning_preservation.status == DimensionStatus.RATED
            and isinstance(ann.meaning_preservation.score, int)
        ]
        if meaning_scores and (max(meaning_scores) - min(meaning_scores) >= 2):
            triggers.append("MEANING_SPREAD_GE_2")

        grammar_scores = [
            ann.grammatical_acceptability.score
            for ann in annotations
            if ann.grammatical_acceptability.status == DimensionStatus.RATED
            and isinstance(ann.grammatical_acceptability.score, int)
        ]
        if grammar_scores and (max(grammar_scores) - min(grammar_scores) >= 2):
            triggers.append("GRAMMAR_SPREAD_GE_2")

        if triggers:
            entry = {
                "item_id": item_id,
                "triggers": sorted(list(set(triggers))),
                "annotation_ids": [ann.annotation_id for ann in annotations],
                "resolved": False,
            }
            self._queue[item_id] = entry
            return entry

        return None

    def record_adjudication(self, record: AdjudicationRecord) -> AdjudicationRecord:
        if record.adjudication_id in self._adjudications:
            raise ValueError(f"Adjudication {record.adjudication_id} already exists.")

        self._adjudications[record.adjudication_id] = record
        if record.item_id in self._queue:
            self._queue[record.item_id]["resolved"] = record.resolved

        # Store in protected storage
        self.storage.store_json(
            "adjudications",
            f"{record.adjudication_id}.json",
            record.model_dump(),
        )

        self.audit.log_event(
            actor_id=record.adjudicator_id,
            action="ADJUDICATION_RESOLVED",
            object_id=record.adjudication_id,
            outcome=record.final_disposition.value,
            details={
                "item_id": record.item_id,
                "resolved": record.resolved,
                "reason_codes": [rc.value for rc in record.reason_codes],
            },
        )

        return record

    def reconcile_adjudication_accounting(self) -> Dict[str, int]:
        """Level 6 Accounting: AdjudicationQueue = Resolved + UnresolvedExpertDisagreement + Pending + Excluded + Unaccounted"""
        total = len(self._queue)
        resolved = 0
        unresolved = 0
        pending = 0

        for item_id, q_item in self._queue.items():
            adjs = [a for a in self._adjudications.values() if a.item_id == item_id]
            if not adjs:
                pending += 1
            else:
                adj = adjs[0]
                if adj.final_disposition == AdjudicationDisposition.UNRESOLVED_EXPERT_DISAGREEMENT:
                    unresolved += 1
                else:
                    resolved += 1

        unaccounted = total - (resolved + unresolved + pending)

        return {
            "total_queue": total,
            "resolved": resolved,
            "unresolved_expert_disagreements": unresolved,
            "pending": pending,
            "excluded_with_reason": 0,
            "unaccounted": unaccounted,
        }
