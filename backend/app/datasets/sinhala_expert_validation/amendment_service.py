"""
Stage 34 — Amendment Management Service
Manages versioned amendment records without overwriting immutable original annotations.
Provides Level 5 zero-loss accounting reconciliation.
"""

from typing import Dict, List, Optional
from .audit import AuditLogger
from .enums import AmendmentStatus
from .protected_storage import ProtectedStorageManager
from .schemas import AmendmentRecord


class AmendmentService:
    def __init__(
        self,
        storage: Optional[ProtectedStorageManager] = None,
        audit: Optional[AuditLogger] = None,
    ):
        self.storage = storage or ProtectedStorageManager()
        self.audit = audit or AuditLogger(self.storage)
        self._amendments: Dict[str, AmendmentRecord] = {}

    def record_amendment(self, amendment: AmendmentRecord) -> AmendmentRecord:
        if amendment.amendment_id in self._amendments:
            raise ValueError(f"Amendment {amendment.amendment_id} already exists.")

        self._amendments[amendment.amendment_id] = amendment

        # Store in protected storage
        self.storage.store_json(
            "amendments",
            f"{amendment.amendment_id}.json",
            amendment.model_dump(),
        )

        self.audit.log_event(
            actor_id=amendment.reviewer_id,
            action="AMENDMENT_RECORDED",
            object_id=amendment.amendment_id,
            outcome=amendment.status.value,
            details={
                "original_annotation_id": amendment.original_annotation_id,
                "item_id": amendment.item_id,
            },
        )

        return amendment

    def get_amendment(self, amendment_id: str) -> Optional[AmendmentRecord]:
        return self._amendments.get(amendment_id)

    def reconcile_amendment_accounting(self) -> Dict[str, int]:
        """Level 5 Accounting: AmendmentRecords = Accepted + Rejected + Withdrawn + Unaccounted"""
        total = len(self._amendments)
        accepted = sum(1 for a in self._amendments.values() if a.status == AmendmentStatus.ACCEPTED)
        rejected = sum(1 for a in self._amendments.values() if a.status == AmendmentStatus.REJECTED)
        withdrawn = sum(1 for a in self._amendments.values() if a.status == AmendmentStatus.WITHDRAWN)
        unaccounted = total - (accepted + rejected + withdrawn)

        return {
            "total_amendments": total,
            "accepted": accepted,
            "rejected": rejected,
            "withdrawn": withdrawn,
            "unaccounted": unaccounted,
        }
