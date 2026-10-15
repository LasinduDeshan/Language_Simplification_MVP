"""
Stage 30 Preprocessing Bridge for Stage 31 External Datasets.
Executes the frozen Stage 30 pipeline, enforces physical storage decoupling,
generates versioned keyed HMAC digests, logs unkeyed hashes to external ledger,
and verifies zero pipeline-introduced U+FFFD.
"""

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from app.sinhala_preprocessing.config import get_frozen_configuration
from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.schemas import SinhalaPreprocessingRecord, TerminalDisposition
from app.datasets.sinhala_external.schemas import StagedDocumentRecord
from app.datasets.sinhala_external.storage import ProtectedStorageManager, storage_manager

HMAC_KEY_ID = "HMAC-2026-V1"
HMAC_KEY_VERSION = 1
DIGEST_INPUT_SCHEMA = "sinhala-pilot-record:v1"

@dataclass(frozen=True)
class PreprocessedBridgeResult:
    record_id: str
    public_record_digest: str
    hmac_key_id: str
    hmac_key_version: int
    digest_input_schema: str
    document_id: str
    source_id: str
    retrieval_id: str
    rights_profile_id: str
    rights_profile_version: int
    document_group_id: str
    source_offset_or_locator: str
    is_method_development_record: bool
    provisional_domain: str
    stage30_disposition: str
    stage30_configuration_hash: str
    normalized_text_storage_ref: str
    sentence_count: int
    token_count: int
    grapheme_count: int
    quality_flags: List[str]
    pipeline_introduced_fffd_count: int
    effective_export_policy: str
    literal_text_redistributable: bool

class Stage30PreprocessingBridge:
    """Bridges staged documents to the frozen Stage 30 preprocessor."""

    def __init__(self, storage: ProtectedStorageManager = storage_manager):
        self.storage = storage
        self.config_data = get_frozen_configuration()
        self.expected_config_hash = self.config_data["configuration_sha256"]
        self.hmac_key = self._get_or_create_hmac_key()
        self.internal_hash_ledger = self.storage.dedup_dir / "internal_hashes.jsonl"

    def _get_or_create_hmac_key(self) -> bytes:
        """Retrieves or creates a secure 256-bit secret HMAC key in protected external storage."""
        env_key = os.environ.get("SINHALA_HMAC_KEY")
        if env_key:
            return bytes.fromhex(env_key)

        key_file = self.storage.dedup_dir / "hmac_secret.key"
        if key_file.exists():
            return bytes.fromhex(key_file.read_text(encoding="utf-8").strip())

        new_key = secrets.token_bytes(32)
        key_file.write_text(new_key.hex() + "\n", encoding="utf-8")
        return new_key

    def compute_keyed_digest(self, record_id: str, normalized_text: str) -> str:
        """Computes keyed HMAC-SHA-256 for public repository digests."""
        msg = f"{DIGEST_INPUT_SCHEMA}:{record_id}:{normalized_text}".encode("utf-8")
        return hmac.new(self.hmac_key, msg, hashlib.sha256).hexdigest()

    def process_staged_document(
        self,
        staged_doc: StagedDocumentRecord,
        doc_seq: int,
        effective_export_policy: str = "PUBLIC_PERMITTED_CC_BY",
        literal_text_redistributable: bool = True
    ) -> PreprocessedBridgeResult:
        record_id = f"SI-PILOT-{doc_seq:06d}"
        
        # Read raw text from external protected storage
        raw_text_bytes = self.storage.read_raw_file(staged_doc.raw_text_storage_ref)
        raw_text = raw_text_bytes.decode("utf-8")

        # Execute frozen Stage 30 pipeline
        prep_res: SinhalaPreprocessingRecord = preprocess_sinhala_text(
            raw_text=raw_text,
            record_id=record_id,
            language="si",
            locale="si-LK",
            text_role="prose"
        )

        # Invariant check: Configuration hash must match frozen Stage 30 configuration
        if prep_res.configuration_sha256 != self.expected_config_hash:
            raise RuntimeError(
                f"Configuration drift detected! Expected {self.expected_config_hash}, got {prep_res.configuration_sha256}"
            )

        # Enforce Invariant 5: Pipeline-introduced U+FFFD must be strictly zero
        raw_fffd_count = raw_text.count("\uFFFD")
        norm_fffd_count = prep_res.normalized_text.count("\uFFFD")
        introduced_fffd = max(0, norm_fffd_count - raw_fffd_count)
        if introduced_fffd > 0:
            raise RuntimeError(f"Pipeline introduced {introduced_fffd} U+FFFD replacement characters into {record_id}")

        # Write normalized text to external protected storage
        norm_filename = f"{record_id}.txt"
        target_path, norm_storage_ref = self.storage.write_raw_file(
            source_id="normalized",
            retrieval_id="pilot",
            filename=norm_filename,
            data=prep_res.normalized_text.encode("utf-8")
        )

        # Log unkeyed text hashes exclusively to external protected integrity ledger
        ledger_entry = {
            "record_id": record_id,
            "document_id": staged_doc.document_id,
            "source_id": staged_doc.source_id,
            "raw_text_sha256": prep_res.raw_text_sha256,
            "normalized_text_sha256": prep_res.normalized_text_sha256,
            "sentence_count": len(prep_res.sentences),
            "token_count": len(prep_res.tokens)
        }
        with open(self.internal_hash_ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(ledger_entry) + "\n")

        # Compute keyed HMAC digest for Git-safe metadata
        public_digest = self.compute_keyed_digest(record_id, prep_res.normalized_text)

        return PreprocessedBridgeResult(
            record_id=record_id,
            public_record_digest=public_digest,
            hmac_key_id=HMAC_KEY_ID,
            hmac_key_version=HMAC_KEY_VERSION,
            digest_input_schema=DIGEST_INPUT_SCHEMA,
            document_id=staged_doc.document_id,
            source_id=staged_doc.source_id,
            retrieval_id=staged_doc.retrieval_id,
            rights_profile_id=staged_doc.rights_profile_id,
            rights_profile_version=staged_doc.rights_profile_version,
            document_group_id=staged_doc.document_group_id,
            source_offset_or_locator=staged_doc.source_offset_or_locator,
            is_method_development_record=staged_doc.is_method_development_unit,
            provisional_domain=staged_doc.provisional_domain,
            stage30_disposition=prep_res.final_disposition.value,
            stage30_configuration_hash=prep_res.configuration_sha256,
            normalized_text_storage_ref=norm_storage_ref,
            sentence_count=len(prep_res.sentences),
            token_count=len(prep_res.tokens),
            grapheme_count=prep_res.normalized_grapheme_count,
            quality_flags=[q.value for q in prep_res.quality_flags],
            pipeline_introduced_fffd_count=introduced_fffd,
            effective_export_policy=effective_export_policy,
            literal_text_redistributable=literal_text_redistributable
        )
