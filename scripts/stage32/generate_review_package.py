"""
Generate Lexicon Review Package and Draft Lexicon Artifacts for Stage 32 (WP8).
Applies provisional banding, builds stratified review queues,
generates public metadata exports, and verifies zero fabricated reviews.
"""

from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry
from app.datasets.sinhala_lexicon.banding import ProvisionalBandingEngine
from app.datasets.sinhala_lexicon.review_service import LexiconReviewService
from app.datasets.sinhala_lexicon.export_service import LexiconExportService
from app.datasets.sinhala_lexicon.parity_analyzer import ParityAnalyzer

CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
DRAFT_LEXICON_FILE = PROJECT_ROOT / "data" / "sinhala_lexicon" / "lexicon" / "draft_lexicon.jsonl"

def main():
    print("=== Generating Stage 32 Review Package and Draft Lexicon ===")
    assert CANDIDATE_LEDGER.exists(), f"Missing candidate ledger: {CANDIDATE_LEDGER}"

    # Load candidates
    candidates = []
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                candidates.append(CandidateLexiconEntry.model_validate_json(line))

    # 1. Compute bounded dispersion for each candidate
    parity_analyzer = ParityAnalyzer()
    candidates_with_dispersion = []
    for c in candidates:
        ds = parity_analyzer.compute_bounded_source_dispersion(
            source_freq_dist=c.source_frequency_distribution,
            eligible_source_count=c.eligible_source_count
        )
        c_updated = c.model_copy(update={"source_dispersion": ds})
        candidates_with_dispersion.append(c_updated)

    # 2. Apply provisional banding
    banding_engine = ProvisionalBandingEngine()
    final_candidates = banding_engine.apply_banding_to_candidates(candidates_with_dispersion)

    # 3. Write draft lexicon
    DRAFT_LEXICON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DRAFT_LEXICON_FILE, "w", encoding="utf-8") as f:
        for c in final_candidates:
            f.write(c.model_dump_json() + "\n")

    print(f"Draft lexicon generated at: {DRAFT_LEXICON_FILE} ({len(final_candidates)} entries)")

    # 4. Generate stratified review queue
    review_svc = LexiconReviewService()
    queue = review_svc.build_stratified_review_queue(final_candidates)

    # 5. Generate public metadata export
    export_svc = LexiconExportService()
    pub_export = export_svc.export_public_metadata(final_candidates)

    # 6. Safety check: verify zero fabricated reviews
    for item in queue:
        tmpl = item["review_template"]
        assert tmpl["reviewer_id"] is None, "Fabricated reviewer_id detected!"
        assert tmpl["reviewed_at"] is None, "Fabricated reviewed_at detected!"
        assert tmpl["lemma_decision"] == "NOT_REVIEWED", "Premature review decision populated!"

    print("=== Expert Review Package and Draft Lexicon Generation Complete ===")

if __name__ == "__main__":
    main()
