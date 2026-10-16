"""
Occurrence Ledger Builder and Accounting Manager for Stage 32.
Extracts all token occurrences from the canonical analytical corpus,
resolves stable entry IDs, serializes token_occurrence_ledger.jsonl,
and guarantees zero-loss occurrence accounting.
"""

import collections
import json
from pathlib import Path
from typing import Dict, List, Tuple

from app.datasets.sinhala_lexicon.corpus_bridge import Stage31CorpusBridge
from app.datasets.sinhala_lexicon.enums import OccurrenceDisposition
from app.datasets.sinhala_lexicon.schemas import TokenOccurrenceRecord

class OccurrenceLedgerBuilder:
    """Orchestrates occurrence extraction and builds the authoritative occurrence ledger."""

    def __init__(self, bridge: Stage31CorpusBridge = None):
        self.bridge = bridge or Stage31CorpusBridge()
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.ledgers_dir = repo_root / "data" / "sinhala_lexicon" / "ledgers"
        self.ledger_file = self.ledgers_dir / "token_occurrence_ledger.jsonl"

    def build_occurrence_ledger(self) -> Tuple[List[TokenOccurrenceRecord], Dict[str, str], dict]:
        """
        Executes a two-pass occurrence extraction:
        1. Pass 1: Collects all surface forms for INCLUDED candidates and assigns deterministic entry IDs.
        2. Pass 2: Emits and writes fully reconciled TokenOccurrenceRecords.
        Returns:
            (occurrence_records, surface_to_entry_id_map, accounting_summary)
        """
        self.ledgers_dir.mkdir(parents=True, exist_ok=True)

        # Pass 1: Identify all distinct candidate surface forms
        surface_counts = collections.Counter()
        print("Pass 1: Scanning canonical records for candidate surface forms...")
        for occ in self.bridge.process_corpus_tokens(entry_id_resolver=None):
            if occ.occurrence_disposition == OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE:
                # Read surface from storage
                surface = occ.context_storage_ref  # Context has snippet, token text has token
                # We can store surface mapping deterministically
                surface_counts[occ.occurrence_id] += 1

        # Deterministic entry ID assignment sorted lexicographically
        # To do this cleanly, let's collect all tokens in memory (150 records is ~10,000 tokens)
        print("Extracting all occurrences across 150 canonical records...")
        raw_occurrences = list(self.bridge.process_corpus_tokens(entry_id_resolver=None))

        # Collect distinct surface forms from protected storage
        from app.datasets.sinhala_lexicon.storage import lexicon_storage
        candidate_surfaces = set()
        surface_map: Dict[str, str] = {}  # occurrence_id -> surface_str

        for occ in raw_occurrences:
            surface = lexicon_storage.read_file_text(occ.token_text_storage_ref)
            surface_map[occ.occurrence_id] = surface
            if occ.occurrence_disposition == OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE:
                candidate_surfaces.add(surface)

        # Deterministic entry ID mapping
        sorted_surfaces = sorted(list(candidate_surfaces))
        surface_to_entry_id: Dict[str, str] = {
            s: f"SI-LEX-{idx:06d}" for idx, s in enumerate(sorted_surfaces, start=1)
        }

        # Pass 2: Assign entry IDs and serialize occurrence ledger
        final_occurrences: List[TokenOccurrenceRecord] = []
        accounting = collections.Counter()

        with open(self.ledger_file, "w", encoding="utf-8") as f:
            for occ in raw_occurrences:
                surface = surface_map[occ.occurrence_id]
                if occ.occurrence_disposition == OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE:
                    entry_id = surface_to_entry_id.get(surface)
                    cand_status = "EXTRACTED"
                    reasons = []
                else:
                    entry_id = None
                    cand_status = "NOT_EXTRACTED"
                    reasons = [occ.exclusion_reason_code] if occ.exclusion_reason_code else []

                # Updated occurrence with assigned entry ID
                resolved_occ = occ.model_copy(update={
                    "entry_id": entry_id,
                    "candidate_extraction_status": cand_status,
                    "reason_codes": reasons,
                    "protected_context_ref": occ.context_storage_ref
                })
                final_occurrences.append(resolved_occ)
                accounting[resolved_occ.occurrence_disposition.value] += 1

                f.write(resolved_occ.model_dump_json() + "\n")

        total_tokens = len(final_occurrences)
        included = accounting[OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE.value]
        excluded = accounting[OccurrenceDisposition.EXCLUDED_TOKEN_CLASS.value]
        review = accounting[OccurrenceDisposition.MANUAL_REVIEW_OCCURRENCE.value]
        rejected = (
            accounting[OccurrenceDisposition.REJECTED_PRIVACY_OR_SECURITY.value] +
            accounting[OccurrenceDisposition.REJECTED_INVALID_SOURCE_EVIDENCE.value]
        )
        unaccounted = total_tokens - (included + excluded + review + rejected)

        accounting_summary = {
            "total_token_occurrences": total_tokens,
            "included_candidate_occurrences": included,
            "excluded_token_class_occurrences": excluded,
            "manual_review_occurrences": review,
            "rejected_occurrences": rejected,
            "unaccounted_occurrences": unaccounted,
            "distinct_candidate_entries": len(sorted_surfaces)
        }

        print(f"Occurrence ledger built successfully: {self.ledger_file}")
        print(f"Total tokens: {total_tokens} | Included: {included} | Excluded: {excluded} | Review: {review} | Distinct candidates: {len(sorted_surfaces)}")
        assert unaccounted == 0, f"Occurrence accounting violation: {unaccounted} unaccounted occurrences!"

        return final_occurrences, surface_to_entry_id, accounting_summary
