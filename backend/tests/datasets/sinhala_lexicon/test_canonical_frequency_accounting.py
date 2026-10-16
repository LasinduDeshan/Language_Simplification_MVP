"""
Tests for Canonical Frequency Accounting in Stage 32 (WP5).
Verifies that primary statistics are computed strictly over the 150 canonical records,
and bounded source dispersion obeys the fixed K entropy formula.
"""

from pathlib import Path
import json
import pytest

from app.datasets.sinhala_lexicon.parity_analyzer import ParityAnalyzer
from app.datasets.sinhala_lexicon.schemas import CandidateLexiconEntry

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"

def test_bounded_source_dispersion_formula():
    """Verify source dispersion calculation handles single source and multi-source distributions."""
    analyzer = ParityAnalyzer()

    # K = 1: returns 0.0 by definition (avoiding log_1)
    d0 = analyzer.compute_bounded_source_dispersion({"SRC-1": 10}, eligible_source_count=1)
    assert d0 == 0.0

    # Single source in K = 5: entropy is 0.0, dispersion = 0.0
    d1 = analyzer.compute_bounded_source_dispersion({"SRC-1": 10}, eligible_source_count=5)
    assert d1 == 0.0

    # Perfectly uniform across all K = 5 sources: dispersion = 1.0
    uniform_dist = {f"SRC-{i}": 10 for i in range(1, 6)}
    d_uniform = analyzer.compute_bounded_source_dispersion(uniform_dist, eligible_source_count=5)
    assert abs(d_uniform - 1.0) < 1e-4

    # Skewed distribution: 0 < dispersion < 1.0
    skewed_dist = {"SRC-1": 8, "SRC-2": 2}
    d_skewed = analyzer.compute_bounded_source_dispersion(skewed_dist, eligible_source_count=5)
    assert 0.0 < d_skewed < 1.0

def test_canonical_frequencies_are_positive_integers():
    """Verify all candidate entries have canonical_frequency >= 1 and document_frequency in [1, 150]."""
    assert CANDIDATE_LEDGER.exists()
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = CandidateLexiconEntry.model_validate_json(line)
            assert entry.canonical_frequency >= 1
            assert 1 <= entry.canonical_document_frequency <= 150
            assert entry.eligible_source_count >= 1
            assert 1 <= entry.observed_source_count <= entry.eligible_source_count


def test_excluded_and_review_occurrences_have_null_entry_id():
    """Verify non-extracted/review occurrences have entry_id is None and never appear in candidate memberships."""
    occ_ledger = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "token_occurrence_ledger.jsonl"
    assert occ_ledger.exists()
    assert CANDIDATE_LEDGER.exists()

    candidate_entry_ids = set()
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = json.loads(line)
                candidate_entry_ids.add(c["entry_id"])

    assert len(candidate_entry_ids) == 1010

    included_count = 0
    excluded_count = 0
    review_count = 0

    with open(occ_ledger, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            disp = rec["occurrence_disposition"]
            if disp in ("EXCLUDED_TOKEN_CLASS", "MANUAL_REVIEW_OCCURRENCE"):
                if disp == "EXCLUDED_TOKEN_CLASS":
                    excluded_count += 1
                else:
                    review_count += 1
                    assert rec["reason_codes"] == ["MIXED_SCRIPT_TOKEN"]

                assert rec["entry_id"] is None
                assert rec["candidate_extraction_status"] == "NOT_EXTRACTED"
                assert rec["protected_context_ref"].startswith("protected://")
                assert rec["entry_id"] not in candidate_entry_ids
            elif disp == "INCLUDED_CANDIDATE_OCCURRENCE":
                included_count += 1
                assert rec["entry_id"] is not None
                assert rec["candidate_extraction_status"] == "EXTRACTED"
                assert rec["entry_id"] in candidate_entry_ids

    assert included_count == 3668
    assert excluded_count == 400
    assert review_count == 4
    assert included_count + excluded_count + review_count == 4072


def test_candidate_review_reason_consistency():
    """Assert exact consistency across empirical quality flags, structured review findings, and review categories."""
    assert CANDIDATE_LEDGER.exists()

    manual_review_required = 0
    sensitive_semantic_review = 0
    complex_or_rare_form_review = 0
    ocr_or_repetition_flag = 0
    low_confidence_morphology = 0

    clean_words = {"කැලේ", "පතුලේ", "ලේකම්වරයා", "ගොඩනැගිල්ලේ"}

    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            disp = entry.get("terminal_entry_disposition")
            flags = entry.get("quality_flags", [])
            findings = entry.get("review_findings", [])
            canonical = entry.get("canonical_form")

            # Verify legitimate Sinhala words are not misclassified
            if canonical in clean_words:
                assert disp == "ACCEPTED_DRAFT_LEXICON_ENTRY"
                assert "OCR_OR_REPETITION_FLAG" not in flags
                assert "POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW" not in flags

            if disp == "MANUAL_REVIEW_REQUIRED":
                manual_review_required += 1
                assert len(findings) >= 1
                for finding in findings:
                    assert finding["reason_code"] in ("POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW", "COMPLEX_OR_RARE_FORM_REVIEW")
                    assert finding["rule_id"].startswith("STAGE32-RULE-")
                    assert "observed_metric" in finding["trigger_evidence"]
                    assert "threshold" in finding["trigger_evidence"]
                    assert len(finding["trigger_evidence"]["source_record_ids"]) > 0
                    assert finding["automated_finding_only"] is True
                    assert finding["human_validated"] is False

            if "POTENTIALLY_SENSITIVE_SEMANTIC_REVIEW" in flags:
                sensitive_semantic_review += 1

            if "COMPLEX_OR_RARE_FORM_REVIEW" in flags:
                complex_or_rare_form_review += 1

            if "OCR_OR_REPETITION_FLAG" in flags or "SUSPECTED_OCR_OR_REPETITION_ARTIFACT" in flags:
                ocr_or_repetition_flag += 1

            if "LOW_CONFIDENCE_MORPHOLOGY" in flags or entry.get("lemma_confidence", 1.0) < 0.6:
                low_confidence_morphology += 1

    assert manual_review_required == 9
    assert sensitive_semantic_review == 3
    assert complex_or_rare_form_review == 6
    assert ocr_or_repetition_flag == 0
    assert low_confidence_morphology == 0

