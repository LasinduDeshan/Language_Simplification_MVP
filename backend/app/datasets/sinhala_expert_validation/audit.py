"""
Stage 34 — Audit Logging Service
Logs administrative and review lifecycle actions without raw source text, candidate text, or PII.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Optional
import uuid

from .protected_storage import ProtectedStorageManager


class AuditLogger:
    def __init__(self, storage_manager: Optional[ProtectedStorageManager] = None):
        self.storage = storage_manager or ProtectedStorageManager()
        self.log_file = self.storage.subdirs["audit"] / "stage34_audit_log.jsonl"

    def log_event(
        self,
        actor_id: str,
        action: str,
        object_id: str,
        outcome: str,
        rule_or_version: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ):
        event = {
            "event_id": f"EVT-{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "action": action,
            "object_id": object_id,
            "outcome": outcome,
            "rule_or_version": rule_or_version,
            "request_id": request_id or str(uuid.uuid4()),
            "details": details or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event
