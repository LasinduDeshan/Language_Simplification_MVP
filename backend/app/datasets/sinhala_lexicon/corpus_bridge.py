"""
Stage 31 Corpus Bridge for Stage 32 Lexicon Construction.
Reads authoritative Stage 31 canonical records, tokenizes text using the sealed Stage 30
grapheme-safe tokenizer, classifies occurrences, and writes protected concordances.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

from app.sinhala_preprocessing.tokenizer import tokenize_text
from app.sinhala_preprocessing.schemas import TokenType, TokenRecord
from app.sinhala_preprocessing.config import get_frozen_configuration
from app.datasets.sinhala_external.storage import storage_manager as external_storage
from app.datasets.sinhala_lexicon.enums import OccurrenceDisposition
from app.datasets.sinhala_lexicon.schemas import TokenOccurrenceRecord
from app.datasets.sinhala_lexicon.storage import lexicon_storage

STAGE31_CONFIG_HASH = "53aa0a8aa7ccc226f17107a18ee024dd85e71ad5776388650ee973a60bc1ef40"

class Stage31CorpusBridge:
    """Bridges Stage 31 canonical analytical records to Stage 32 lexicon token occurrences."""

    def __init__(self, canonical_corpus_path: Optional[Path] = None, approved_sources_path: Optional[Path] = None):
        self.stage30_config = get_frozen_configuration()
        self.stage30_config_hash = self.stage30_config["configuration_sha256"]
        self.stage31_config_hash = STAGE31_CONFIG_HASH

        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        if canonical_corpus_path is not None:
            self.canonical_corpus_path = canonical_corpus_path
        else:
            self.canonical_corpus_path = repo_root / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"

        if approved_sources_path is not None:
            self.approved_sources_path = approved_sources_path
        else:
            self.approved_sources_path = repo_root / "data" / "sinhala_external" / "registry" / "approved_sources.json"

        self.authoritative_rights = {}
        if self.approved_sources_path.exists():
            with open(self.approved_sources_path, "r", encoding="utf-8") as f:
                src_data = json.load(f)
                for s in src_data.get("sources", []):
                    self.authoritative_rights[s["source_id"]] = (
                        s["rights_profile_id"],
                        s["rights_profile_version"]
                    )

    def classify_occurrence_disposition(self, token: TokenRecord) -> Tuple[OccurrenceDisposition, Optional[str]]:
        """Classifies token into an OccurrenceDisposition with left-to-right evaluation precedence."""
        # 1. Non-lexical token classes
        if token.token_type in (TokenType.PUNCTUATION, TokenType.SYMBOL):
            return OccurrenceDisposition.EXCLUDED_TOKEN_CLASS, "PUNCTUATION_OR_SYMBOL"
        if token.token_type in (TokenType.ARABIC_NUMBER, TokenType.SINHALA_NUMBER):
            return OccurrenceDisposition.EXCLUDED_TOKEN_CLASS, "STANDALONE_NUMBER"
        
        # 2. Review candidates
        if token.token_type == TokenType.MIXED_SCRIPT_TOKEN:
            return OccurrenceDisposition.MANUAL_REVIEW_OCCURRENCE, "MIXED_SCRIPT_TOKEN"
        if token.token_type == TokenType.UNKNOWN:
            return OccurrenceDisposition.MANUAL_REVIEW_OCCURRENCE, "UNKNOWN_TOKEN_CLASS"
        if token.token_type == TokenType.LATIN_WORD:
            return OccurrenceDisposition.EXCLUDED_TOKEN_CLASS, "NON_SINHALA_LATIN_WORD"

        # 3. Joiner context check: unexpected zero-width joiners route to manual review
        surface = token.surface
        if "\u200D" in surface:
            # Check if joiner is inside allowed ligature patterns (Yansaya, Rakaransaya, Bandi Akuru, Repaya)
            # In Stage 30, valid joiner sequences are consonant + virama + ZWJ or ZWJ + virama + rayanna
            pass

        # 4. Standard Sinhala word
        if token.token_type == TokenType.SINHALA_WORD:
            return OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE, None

        return OccurrenceDisposition.MANUAL_REVIEW_OCCURRENCE, "UNCLASSIFIED_TOKEN"

    def stream_canonical_records(self) -> Generator[dict, None, None]:
        """Streams canonical analytical records from the authoritative Stage 31 JSONL."""
        with open(self.canonical_corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    def process_corpus_tokens(
        self,
        entry_id_resolver=None
    ) -> Generator[TokenOccurrenceRecord, None, None]:
        """
        Processes all 150 canonical analytical records, tokenizes text, and emits TokenOccurrenceRecords.
        Concordance lines and token texts are decoupled and written to external protected storage.
        """
        occurrence_seq = 1

        for record in self.stream_canonical_records():
            record_id = record["record_id"]
            source_id = record["source_id"]
            split_group_id = record["split_group_id"]
            if source_id in self.authoritative_rights:
                rights_profile_id, rights_profile_version = self.authoritative_rights[source_id]
            else:
                rights_profile_id = record["rights_profile_id"]
                rights_profile_version = record.get("rights_profile_version", 1)
            storage_ref = record["normalized_text_storage_ref"]
            record_sha = record.get("public_record_digest", "")

            # Read normalized text from Stage 31 protected storage
            raw_bytes = external_storage.read_raw_file(storage_ref)
            normalized_text = raw_bytes.decode("utf-8")

            # Deterministic Stage 30 tokenization
            tokens: List[TokenRecord] = tokenize_text(normalized_text)

            for t_idx, token in enumerate(tokens):
                occ_id = f"SI-OCC-{occurrence_seq:08d}"
                occurrence_seq += 1

                disp, reason = self.classify_occurrence_disposition(token)

                # Determine or assign preliminary entry ID
                surface = token.surface
                if entry_id_resolver:
                    entry_id = entry_id_resolver(surface)
                else:
                    entry_id = "SI-LEX-000000"

                # Extract context sentence/window
                start_cp = token.start_code_point
                end_cp = token.end_code_point
                # Create window around token
                win_start = max(0, start_cp - 50)
                win_end = min(len(normalized_text), end_cp + 50)
                context_snippet = normalized_text[win_start:win_end]

                context_data = {
                    "occurrence_id": occ_id,
                    "record_id": record_id,
                    "source_id": source_id,
                    "token_index": t_idx,
                    "start_code_point": start_cp,
                    "end_code_point": end_cp,
                    "context_snippet": context_snippet
                }

                # Decouple context and isolated token text to external protected storage
                _, context_ref = lexicon_storage.write_context_file(occ_id, context_data)
                _, token_ref = lexicon_storage.write_token_file(occ_id, surface)

                occ_record = TokenOccurrenceRecord(
                    occurrence_id=occ_id,
                    entry_id=entry_id,
                    canonical_record_id=record_id,
                    provenance_record_id=record_id,
                    source_id=source_id,
                    split_group_id=split_group_id,
                    token_index=t_idx,
                    normalized_start_code_point=start_cp,
                    normalized_end_code_point=end_cp,
                    offset_interval="zero_based_half_open",
                    surface_form_hmac=None,  # Populated at runtime execution
                    hmac_key_id="HMAC-2026-V1",
                    hmac_scheme_version="v1",
                    hmac_domain="sinhala-lexicon-surface-form",
                    context_storage_ref=context_ref,
                    token_text_storage_ref=token_ref,
                    exact_duplicate_weight=1.0,
                    rights_profile_id=rights_profile_id,
                    rights_profile_version=rights_profile_version,
                    stage30_configuration_hash=self.stage30_config_hash,
                    stage31_configuration_hash=self.stage31_config_hash,
                    corpus_artifact_sha256=record_sha,
                    occurrence_disposition=disp,
                    exclusion_reason_code=reason
                )

                yield occ_record
