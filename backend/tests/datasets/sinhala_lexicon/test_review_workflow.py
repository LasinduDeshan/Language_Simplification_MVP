"""
Tests for Expert Review Workflow and Zero-Fabricated-Reviews Invariant in Stage 32 (WP8).
Verifies that all entries in review queues retain unpopulated reviewer identities and review dates.
"""

from pathlib import Path
import json
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
REVIEW_QUEUE_FILE = PROJECT_ROOT / "data" / "sinhala_lexicon" / "lexicon" / "review_queue.jsonl"
DRAFT_LEXICON_FILE = PROJECT_ROOT / "data" / "sinhala_lexicon" / "lexicon" / "draft_lexicon.jsonl"

def test_review_queue_preserves_zero_fabricated_reviews():
    """Verify all 1010 review templates contain null reviewer IDs and null review timestamps."""
    assert REVIEW_QUEUE_FILE.exists(), f"Missing review queue: {REVIEW_QUEUE_FILE}"
    count = 0
    with open(REVIEW_QUEUE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            tmpl = item["review_template"]
            assert tmpl["reviewer_id"] is None, f"Found non-null reviewer_id in {item['entry_id']}"
            assert tmpl["reviewed_at"] is None, f"Found non-null reviewed_at in {item['entry_id']}"
            assert tmpl["lemma_decision"] == "NOT_REVIEWED"
            assert tmpl["age_band_decision"] == "NOT_REVIEWED"
            count += 1
    assert count == 1010

def test_draft_lexicon_governance_flags_remain_false():
    """Verify all draft lexicon entries retain expert_validated=False and approved_for_child_delivery=False."""
    assert DRAFT_LEXICON_FILE.exists()
    count = 0
    with open(DRAFT_LEXICON_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            assert entry["validation_status"] == "draft"
            assert entry["expert_validated"] is False
            assert entry["approved_for_child_delivery"] is False
            assert entry["requires_expert_review"] is True
            count += 1
    assert count == 1010
