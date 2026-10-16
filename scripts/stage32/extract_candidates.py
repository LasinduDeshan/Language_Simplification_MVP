"""
Stage 32 Candidate Lexicon Entry Extraction Script (WP3).
Reads token_occurrence_ledger.jsonl, extracts CandidateLexiconEntry objects,
applies quality routing, serializes candidate_entry_ledger.jsonl, and reconciles entry accounting.
"""

import collections
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_lexicon.candidate_extractor import CandidateExtractor
from app.datasets.sinhala_lexicon.schemas import TokenOccurrenceRecord
from app.datasets.sinhala_lexicon.storage import lexicon_storage
from app.datasets.sinhala_lexicon.enums import TerminalEntryDisposition

OCCURRENCE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "token_occurrence_ledger.jsonl"
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
ACCOUNTING_OUTPUT = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_accounting.json"

def main():
    print("=== Running Stage 32 Candidate Lexicon Extraction ===")
    assert OCCURRENCE_LEDGER.exists(), f"Occurrence ledger missing: {OCCURRENCE_LEDGER}"

    # Load occurrences
    occurrences = []
    surface_texts = {}
    surface_to_id = {}

    with open(OCCURRENCE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = TokenOccurrenceRecord.model_validate_json(line)
            occurrences.append(rec)
            # Read token text from protected storage
            txt = lexicon_storage.read_file_text(rec.token_text_storage_ref)
            surface_texts[rec.occurrence_id] = txt
            if rec.entry_id != "SI-LEX-000000":
                surface_to_id[txt] = rec.entry_id

    extractor = CandidateExtractor()
    candidates = extractor.extract_candidate_entries(
        occurrences=occurrences,
        surface_to_id=surface_to_id,
        surface_texts=surface_texts
    )

    # Reconcile entry dispositions
    accounting = collections.Counter()
    with open(CANDIDATE_LEDGER, "w", encoding="utf-8") as f:
        for c in candidates:
            accounting[c.terminal_entry_disposition.value] += 1
            f.write(c.model_dump_json() + "\n")

    total_candidates = len(candidates)
    accepted = accounting[TerminalEntryDisposition.ACCEPTED_DRAFT_LEXICON_ENTRY.value]
    review = accounting[TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED.value]
    non_lexical = accounting[TerminalEntryDisposition.EXCLUDED_NON_LEXICAL.value]
    non_sinhala = accounting[TerminalEntryDisposition.EXCLUDED_NON_SINHALA.value]
    rejected = (
        accounting[TerminalEntryDisposition.REJECTED_PRIVACY_OR_SECURITY.value] +
        accounting[TerminalEntryDisposition.REJECTED_INVALID_SOURCE_EVIDENCE.value]
    )
    unaccounted = total_candidates - (accepted + review + non_lexical + non_sinhala + rejected)

    summary = {
        "total_extracted_candidates": total_candidates,
        "accepted_draft_entries": accepted,
        "manual_review_required_entries": review,
        "excluded_non_lexical_entries": non_lexical,
        "excluded_non_sinhala_entries": non_sinhala,
        "rejected_entries": rejected,
        "unaccounted_entries": unaccounted
    }

    with open(ACCOUNTING_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Candidates serialized to: {CANDIDATE_LEDGER}")
    print(f"Total: {total_candidates} | Accepted: {accepted} | Review: {review} | Excluded Non-Lexical: {non_lexical}")
    print(f"Unaccounted candidates: {unaccounted}")
    assert unaccounted == 0, f"Candidate accounting violation: {unaccounted} unaccounted candidates"

if __name__ == "__main__":
    main()
