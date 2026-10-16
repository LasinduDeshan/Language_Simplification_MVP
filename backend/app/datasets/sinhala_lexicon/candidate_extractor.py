"""
Candidate Extractor for Stage 32 Sinhala Child-Vocabulary Lexicon.
Aggregates token occurrences into candidate entry items, computes frequencies,
evaluates quality flags, and assigns terminal entry dispositions.
"""

import collections
import json
from pathlib import Path
from typing import Dict, List, Tuple

from app.datasets.sinhala_lexicon.enums import (
    OccurrenceDisposition,
    TerminalEntryDisposition,
    ProvisionalVocabularyBand,
    LemmaMethod,
    FieldExportPolicy
)
from app.datasets.sinhala_lexicon.schemas import (
    CandidateLexiconEntry,
    SurfaceFormRecord,
    RightsProfileReference,
    TokenOccurrenceRecord
)
from app.datasets.sinhala_lexicon.quality_router import LexiconQualityRouter
from app.sinhala_preprocessing.graphemes import segment_graphemes

class CandidateExtractor:
    """Extracts candidate lexicon entries from token occurrences."""

    def __init__(self, quality_router: LexiconQualityRouter = None):
        self.router = quality_router or LexiconQualityRouter()

    def extract_candidate_entries(
        self,
        occurrences: List[TokenOccurrenceRecord],
        surface_to_id: Dict[str, str],
        surface_texts: Dict[str, str],
        rights_map: Dict[str, str] = None
    ) -> List[CandidateLexiconEntry]:
        """
        Groups INCLUDED_CANDIDATE_OCCURRENCE tokens by entry_id,
        calculates preliminary frequencies and dispersion features,
        and constructs CandidateLexiconEntry models.
        """
        # Group occurrences by entry_id
        entry_occurrences = collections.defaultdict(list)
        entry_surfaces = collections.defaultdict(set)

        for occ in occurrences:
            if occ.occurrence_disposition == OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE:
                entry_occurrences[occ.entry_id].append(occ)
                surface = surface_texts.get(occ.occurrence_id, "")
                entry_surfaces[occ.entry_id].add(surface)

        # Total distinct sources in the canonical analytical corpus
        all_canonical_sources = set(occ.source_id for occ in occurrences)
        eligible_source_count = max(1, len(all_canonical_sources))

        candidate_entries: List[CandidateLexiconEntry] = []

        # Sort entry_ids deterministically
        for entry_id in sorted(entry_occurrences.keys()):
            occs = entry_occurrences[entry_id]
            surfaces = list(entry_surfaces[entry_id])
            canonical_form = surfaces[0] if surfaces else ""

            # Calculate frequency metrics
            canonical_freq = len(occs)
            canonical_doc_freq = len(set(o.canonical_record_id for o in occs))
            weighted_freq = sum(getattr(o, "duplicate_weight_float", getattr(o, "exact_duplicate_weight", 1.0)) for o in occs)

            # Source distribution
            src_counts = collections.Counter(o.source_id for o in occs)
            source_count = len(src_counts)

            # Compute grapheme and code-point counts
            graphemes = segment_graphemes(canonical_form)
            grapheme_count = len(graphemes)
            code_point_count = len(canonical_form)

            # Syllable proxy: heuristic based on vowel markers and non-virama consonants
            # Each independent vowel or consonant without virama is a syllable proxy
            syllable_count = max(1, len([g for g in graphemes if "\u0DCA" not in g]))

            # Source record ids contributing to this candidate
            source_record_ids = sorted(list(set(o.provenance_record_id for o in occs)))

            # Screen quality with evidence-based router
            quality_flags, review_findings, is_proper, is_sensitive = self.router.screen_surface_form(
                surface=canonical_form,
                code_point_count=code_point_count,
                grapheme_count=grapheme_count,
                source_record_ids=source_record_ids
            )

            # Rights references
            unique_rights = set((o.source_id, o.rights_profile_id, o.rights_profile_version) for o in occs)
            rights_refs = [
                RightsProfileReference(source_id=s, rights_profile_id=rp, rights_profile_version=v)
                for s, rp, v in sorted(unique_rights)
            ]

            # Terminal disposition determination
            if review_findings:
                disp = TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED
            elif "LEADING_COMBINING_MARK_ERROR" in quality_flags:
                disp = TerminalEntryDisposition.EXCLUDED_NON_LEXICAL
            else:
                disp = TerminalEntryDisposition.ACCEPTED_DRAFT_LEXICON_ENTRY

            # Initial surface form record
            sf_record = SurfaceFormRecord(
                surface_form=canonical_form,
                canonical_frequency=canonical_freq,
                canonical_document_frequency=canonical_doc_freq,
                weighted_provenance_frequency=round(weighted_freq, 6)
            )

            # Field-level export policy
            field_policies = {
                "canonical_form": FieldExportPolicy.PUBLIC_PERMITTED_STANDALONE,
                "frequency_statistics": FieldExportPolicy.PUBLIC_PERMITTED_AGGREGATE,
                "definitions": FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL,
                "concordance_contexts": FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL
            }

            entry = CandidateLexiconEntry(
                entry_id=entry_id,
                language="si",
                locale="si-LK",
                script="Sinh",
                canonical_form=canonical_form,
                candidate_lemma=canonical_form,
                lemma_method=LemmaMethod.IDENTITY_CANONICAL,
                lemma_confidence=1.0,
                surface_forms=[sf_record],
                token_class="SINHALA_WORD",
                grapheme_count=grapheme_count,
                code_point_count=code_point_count,
                syllable_proxy_count=syllable_count,
                canonical_frequency=canonical_freq,
                canonical_document_frequency=canonical_doc_freq,
                weighted_provenance_frequency=round(weighted_freq, 6),
                source_count=source_count,
                source_frequency_distribution=dict(src_counts),
                eligible_source_count=eligible_source_count,
                observed_source_count=source_count,
                source_dispersion=0.0,  # Computed in WP5
                dispersion_formula_version="fixed_k_entropy_v1",
                provisional_band=ProvisionalVocabularyBand.REVIEW_REQUIRED,  # Assigned in WP6
                band_confidence=0.0,
                quality_flags=quality_flags,
                review_findings=review_findings,
                rights_profile_refs=rights_refs,
                field_export_policies=field_policies,
                terminal_entry_disposition=disp,
                validation_status="draft",
                expert_validated=False,
                research_eligible=False,
                approved_for_child_delivery=False,
                approved_for_unsupervised_child_delivery=False,
                requires_expert_review=True
            )
            candidate_entries.append(entry)

        return candidate_entries
