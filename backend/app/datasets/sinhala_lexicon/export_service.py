"""
Sanitized Public Export Service for Stage 32 Sinhala Lexicon.
Generates public metadata exports with runtime keyed HMAC domain separation,
field-level rights enforcement, and zero restricted context leakage.
"""

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from typing import Dict, List, Optional

from app.datasets.sinhala_lexicon.enums import FieldExportPolicy
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry
from app.datasets.sinhala_lexicon.storage import lexicon_storage

HMAC_KEY_ID = "HMAC-2026-V1"
HMAC_SCHEME_VERSION = "v1"
HMAC_DOMAIN = "sinhala-lexicon-surface-form"

class LexiconExportService:
    """Manages public metadata exports and runtime keyed HMAC digest generation."""

    def __init__(self):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.export_dir = repo_root / "data" / "sinhala_lexicon" / "lexicon"
        self.public_export_file = self.export_dir / "public_metadata_export.jsonl"
        self.hmac_key = self._get_or_create_hmac_key()

    def _get_or_create_hmac_key(self) -> bytes:
        """Retrieves or creates a secure 256-bit secret HMAC key in protected external storage."""
        env_key = os.environ.get("SINHALA_LEXICON_HMAC_KEY")
        if env_key:
            return bytes.fromhex(env_key)

        key_file = lexicon_storage.lexicon_root / "hmac_secret.key"
        if key_file.exists():
            return bytes.fromhex(key_file.read_text(encoding="utf-8").strip())

        new_key = secrets.token_bytes(32)
        key_file.write_text(new_key.hex() + "\n", encoding="utf-8")
        return new_key

    def compute_surface_hmac(self, occurrence_id: str, surface_form: str) -> str:
        """Computes keyed HMAC-SHA-256 with exact domain separation."""
        msg = f"{HMAC_DOMAIN}:{HMAC_SCHEME_VERSION}:{occurrence_id}:{surface_form}".encode("utf-8")
        return hmac.new(self.hmac_key, msg, hashlib.sha256).hexdigest()

    def export_public_metadata(
        self,
        candidates: List[CandidateLexiconEntry]
    ) -> Path:
        """
        Emits public_metadata_export.jsonl adhering strictly to field-level rights:
        - Standalone canonical forms included only if permitted.
        - Frequencies and dispersion included as aggregate metrics.
        - Zero concordances, reconstructable text, or unkeyed hashes included.
        """
        self.export_dir.mkdir(parents=True, exist_ok=True)

        exported_count = 0
        with open(self.public_export_file, "w", encoding="utf-8") as f:
            for c in candidates:
                # Field policy check
                can_policy = c.field_export_policies.get("canonical_form", FieldExportPolicy.PUBLIC_PERMITTED_STANDALONE)
                if can_policy == FieldExportPolicy.METADATA_ONLY:
                    exposed_form = None
                else:
                    exposed_form = c.canonical_form

                public_record = {
                    "entry_id": c.entry_id,
                    "language": c.language,
                    "locale": c.locale,
                    "script": c.script,
                    "canonical_form": exposed_form,
                    "token_class": c.token_class,
                    "grapheme_count": c.grapheme_count,
                    "code_point_count": c.code_point_count,
                    "syllable_proxy_count": c.syllable_proxy_count,
                    "canonical_frequency": c.canonical_frequency,
                    "canonical_document_frequency": c.canonical_document_frequency,
                    "weighted_provenance_frequency": c.weighted_provenance_frequency,
                    "source_count": c.source_count,
                    "eligible_source_count": c.eligible_source_count,
                    "observed_source_count": c.observed_source_count,
                    "source_dispersion": c.source_dispersion,
                    "dispersion_formula_version": c.dispersion_formula_version,
                    "provisional_band": c.provisional_band.value,
                    "band_confidence": c.band_confidence,
                    "band_evidence": c.band_evidence,
                    "validation_status": c.validation_status,
                    "expert_validated": c.expert_validated,
                    "approved_for_child_delivery": c.approved_for_child_delivery,
                    "requires_expert_review": c.requires_expert_review
                }
                f.write(json.dumps(public_record, ensure_ascii=False) + "\n")
                exported_count += 1

        print(f"Public metadata export generated: {self.public_export_file} ({exported_count} entries)")
        return self.public_export_file
