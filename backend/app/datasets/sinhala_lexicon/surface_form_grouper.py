"""
Surface Form Grouper and Morphology Hypothesis Engine for Stage 32.
Preserves observed surface forms independently of candidate lemmas,
records grouping edges, confidence scores, and rule versions,
and serializes surface_form_mapping.jsonl.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from app.datasets.sinhala_lexicon.morphology_analyzer import MorphologyAnalyzer
from app.datasets.sinhala_lexicon.schemas import (
    CandidateLexiconEntry,
    SurfaceFormMappingRecord,
    SurfaceFormRecord
)
from app.datasets.sinhala_lexicon.enums import LemmaMethod, TerminalEntryDisposition

class SurfaceFormGrouper:
    """Manages surface form preservation and morphology grouping."""

    def __init__(self, analyzer: MorphologyAnalyzer = None):
        self.analyzer = analyzer or MorphologyAnalyzer()
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.mapping_file = repo_root / "data" / "sinhala_lexicon" / "ledgers" / "surface_form_mapping.jsonl"

    def apply_morphology_and_build_mappings(
        self,
        candidate_entries: List[CandidateLexiconEntry]
    ) -> Tuple[List[CandidateLexiconEntry], List[SurfaceFormMappingRecord]]:
        """
        Analyzes each candidate entry, generates lemma and inflectional hypotheses,
        and serializes the authoritative surface form mapping ledger.
        """
        mappings: List[SurfaceFormMappingRecord] = []
        updated_entries: List[CandidateLexiconEntry] = []

        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.mapping_file, "w", encoding="utf-8") as f:
            for entry in candidate_entries:
                surface = entry.canonical_form
                lemma, method, conf, hypotheses = self.analyzer.analyze_candidate(surface)

                # Determine if disposition should route to review due to low lemma confidence
                disp = entry.terminal_entry_disposition
                if method != LemmaMethod.IDENTITY_CANONICAL and conf < 0.70:
                    disp = TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED

                # Create updated entry
                updated = entry.model_copy(update={
                    "candidate_lemma": lemma,
                    "lemma_method": method,
                    "lemma_confidence": conf,
                    "morphology_hypotheses": hypotheses,
                    "terminal_entry_disposition": disp
                })
                updated_entries.append(updated)

                # Primary mapping record
                rule_id = hypotheses[0].rule_id if hypotheses else "IDENTITY_RULE"
                mapping = SurfaceFormMappingRecord(
                    surface_form=surface,
                    canonical_form=lemma or surface,
                    entry_id=entry.entry_id,
                    morphology_rule_id=rule_id,
                    rule_version=MorphologyAnalyzer.RULE_VERSION,
                    mapping_confidence=conf,
                    is_base_form=(surface == lemma),
                    canonical_frequency=entry.canonical_frequency,
                    canonical_document_frequency=entry.canonical_document_frequency,
                    weighted_provenance_frequency=entry.weighted_provenance_frequency
                )
                mappings.append(mapping)
                f.write(mapping.model_dump_json() + "\n")

        print(f"Surface form mapping ledger written to: {self.mapping_file}")
        print(f"Total mappings: {len(mappings)} | With hypotheses: {len([m for m in mappings if not m.is_base_form])}")

        return updated_entries, mappings
