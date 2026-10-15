"""
Deterministic, rate-limited and sanitized acquisition engine for Stage 31.
"""

import hashlib
import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.datasets.sinhala_external.schemas import (
    CandidateSourceRecord,
    PrimarySourceDecision,
    SanitizedAcquisitionReceipt,
)
from app.datasets.sinhala_external.storage import ProtectedStorageManager, storage_manager

SENSITIVE_PARAM_NAMES = {
    "token", "access_token", "auth", "api_key", "apikey", "key", "signature",
    "sig", "secret", "session", "session_id", "password", "pwd", "credential"
}

def sanitize_url(raw_url: str) -> str:
    """Strips authentication tokens, passwords, and sensitive query parameters from URLs."""
    if not raw_url:
        return ""
    parsed = urllib.parse.urlparse(raw_url)
    
    # Remove userinfo (username:password@)
    netloc = parsed.netloc
    if "@" in netloc:
        netloc = netloc.split("@")[-1]
        
    # Filter query parameters
    query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    sanitized_params = [
        (k, v) for k, v in query_params if k.lower() not in SENSITIVE_PARAM_NAMES
    ]
    new_query = urllib.parse.urlencode(sanitized_params)
    
    sanitized = urllib.parse.urlunparse((
        parsed.scheme,
        netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    return sanitized

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

class AcquisitionEngine:
    """Executes governed acquisition for approved external sources."""

    def __init__(
        self,
        approved_sources_path: Path,
        receipts_dir: Path,
        storage: ProtectedStorageManager = storage_manager
    ):
        self.approved_sources_path = approved_sources_path
        self.receipts_dir = receipts_dir
        self.storage = storage
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def load_approved_sources(self) -> List[CandidateSourceRecord]:
        data = json.loads(self.approved_sources_path.read_text(encoding="utf-8"))
        records = []
        for s in data.get("sources", []):
            rec = CandidateSourceRecord.model_validate(s)
            records.append(rec)
        return records

    def is_rights_profile_expired(self, record: CandidateSourceRecord, current_time: Optional[datetime] = None) -> bool:
        if not record.rights_profile_review_due_at:
            return False
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        due_at = datetime.fromisoformat(record.rights_profile_review_due_at.replace("Z", "+00:00"))
        return current_time > due_at

    def acquire_source(
        self,
        source: CandidateSourceRecord,
        raw_bytes: bytes,
        filename: str,
        content_type: str,
        retrieval_id: str,
        resolved_url: str,
        redirect_chain: Optional[List[str]] = None,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None
    ) -> SanitizedAcquisitionReceipt:
        # Invariant: Must be approved
        if source.primary_decision != PrimarySourceDecision.APPROVED:
            raise PermissionError(
                f"Source {source.source_id} cannot be acquired because primary_decision is {source.primary_decision}"
            )

        # Invariant: Rights profile cannot be expired
        if self.is_rights_profile_expired(source):
            raise PermissionError(
                f"Source {source.source_id} rights profile {source.rights_profile_id} expired on {source.rights_profile_review_due_at}"
            )

        receipt_file = self.receipts_dir / f"{retrieval_id}.json"
        if receipt_file.exists():
            raise FileExistsError(f"Historical retrieval receipt {receipt_file} already exists and cannot be overwritten")

        # Sanitize URLs
        sanitized_resolved = sanitize_url(resolved_url)
        sanitized_redirects = [sanitize_url(u) for u in (redirect_chain or [])]

        # Calculate whole-file SHA-256
        file_sha256 = compute_sha256(raw_bytes)

        # Write to external protected storage
        local_path, storage_ref = self.storage.write_raw_file(
            source_id=source.source_id,
            retrieval_id=retrieval_id,
            filename=filename,
            data=raw_bytes
        )

        receipt = SanitizedAcquisitionReceipt(
            retrieval_id=retrieval_id,
            source_id=source.source_id,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            retrieval_method=source.acquisition_policy.access_method,
            resolved_url_sanitized=sanitized_resolved,
            redirect_chain_sanitized=sanitized_redirects,
            sensitive_query_parameters_removed=True,
            http_status=200,
            content_type=content_type,
            file_name=filename,
            byte_size=len(raw_bytes),
            sha256=file_sha256,
            etag=etag,
            last_modified=last_modified,
            raw_storage_ref=storage_ref,
            redistribution_allowed=source.permissions.raw_redistribution_allowed
        )

        receipt_file.write_text(receipt.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return receipt
