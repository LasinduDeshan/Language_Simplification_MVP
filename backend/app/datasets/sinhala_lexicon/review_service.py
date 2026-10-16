"""
Expert Review and Adjudication Package Preparation Service for Stage 32.
Prepares stratified review queues, rubrics, and independent review schemas
without populating fabricated human expert reviews.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from app.datasets.sinhala_lexicon.enums import (
    ProvisionalVocabularyBand,
    TerminalEntryDisposition,
    ReviewDecision,
    AgeBandReviewDecision
)
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry, LexiconExpertReviewRecord

class LexiconReviewService:
    """Prepares stratified review packages and guarantees zero fabricated human reviews."""

    def __init__(self):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.lexicon_dir = repo_root / "data" / "sinhala_lexicon" / "lexicon"
        self.review_queue_file = self.lexicon_dir / "review_queue.jsonl"

    def build_stratified_review_queue(
        self,
        candidates: List[CandidateLexiconEntry]
    ) -> List[dict]:
        """
        Stratifies candidates into priority review tiers:
        Tier 1: High Priority (Quality flags, sensitive terms, or multi-rule ties)
        Tier 2: Foundational & Early candidates (critical for early language model)
        Tier 3: Developing & Advanced candidates
        Tier 4: Routine candidates
        """
        self.lexicon_dir.mkdir(parents=True, exist_ok=True)
        review_items = []

        for c in candidates:
            # Determine review priority
            if c.terminal_entry_disposition == TerminalEntryDisposition.MANUAL_REVIEW_REQUIRED or c.quality_flags:
                priority = "P1_URGENT_REVIEW"
                review_reason = "quality_flags_or_sensitive_vocabulary"
            elif c.provisional_band == ProvisionalVocabularyBand.FOUNDATIONAL_CANDIDATE:
                priority = "P2_FOUNDATIONAL_VOCABULARY"
                review_reason = "high_frequency_core_child_candidate"
            elif c.provisional_band == ProvisionalVocabularyBand.EARLY_CANDIDATE:
                priority = "P3_EARLY_VOCABULARY"
                review_reason = "moderate_high_frequency_candidate"
            else:
                priority = "P4_STANDARD_VOCABULARY"
                review_reason = "standard_lexical_candidate"

            # Clean unpopulated review template
            review_template = LexiconExpertReviewRecord(
                entry_id=c.entry_id,
                reviewer_id=None,
                independent_review_round=1,
                lemma_decision=ReviewDecision.NOT_REVIEWED,
                age_band_decision=AgeBandReviewDecision.NOT_REVIEWED,
                meaning_review_status=ReviewDecision.NOT_REVIEWED,
                safety_status=ReviewDecision.NOT_REVIEWED,
                comments_storage_ref=None,
                reviewed_at=None
            )

            queue_item = {
                "entry_id": c.entry_id,
                "canonical_form": c.canonical_form,
                "candidate_lemma": c.candidate_lemma,
                "priority_tier": priority,
                "review_reason": review_reason,
                "canonical_frequency": c.canonical_frequency,
                "provisional_band": c.provisional_band.value,
                "quality_flags": c.quality_flags,
                "review_findings": [f.model_dump() for f in c.review_findings],
                "review_finding": c.review_findings[0].model_dump() if c.review_findings else None,
                "review_template": review_template.model_dump()
            }
            review_items.append(queue_item)

        # Sort queue by priority tier
        review_items.sort(key=lambda x: (x["priority_tier"], -x["canonical_frequency"]))

        with open(self.review_queue_file, "w", encoding="utf-8") as f:
            for item in review_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print(f"Stratified review queue generated at: {self.review_queue_file} ({len(review_items)} items)")
        return review_items
