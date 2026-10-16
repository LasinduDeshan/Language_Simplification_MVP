"""
Tests for Stage 32 Ancestry Contract, Schema Invariants, and Review Validation Rules (WP0/WP1).
"""

import subprocess
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.datasets.sinhala_lexicon.enums import (
    OccurrenceDisposition,
    TerminalEntryDisposition,
    ProvisionalVocabularyBand,
    LemmaMethod,
    ReviewDecision,
    AgeBandReviewDecision,
    FieldExportPolicy
)
from app.datasets.sinhala_lexicon.schemas import (
    CandidateLexiconEntry,
    TokenOccurrenceRecord,
    SurfaceFormRecord,
    MorphologyHypothesis,
    RightsProfileReference,
    LexiconExpertReviewRecord
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def git_rev_parse(rev: str) -> str:
    res = subprocess.run(["git", "rev-parse", rev], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
    return res.stdout.strip()

def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    res = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=PROJECT_ROOT, capture_output=True, text=True)
    return res.returncode == 0

def test_prerequisite_commit_and_tag_identity():
    """Verify stage-31-complete-v8 matches authoritative prerequisite commit."""
    expected = "9096cfbf5d6e237c388e6c306dc12f13023875ba"
    c31_v8 = git_rev_parse("stage-31-complete-v8^{commit}")
    assert c31_v8 == expected, f"Authoritative prerequisite commit mismatch: expected {expected}, got {c31_v8}"

def test_stage32_start_tag_pinned_to_prerequisite():
    """Verify stage-32-start tag is pinned to unchanged prerequisite commit."""
    c31_v8 = git_rev_parse("stage-31-complete-v8^{commit}")
    c32_start = git_rev_parse("stage-32-start^{commit}")
    assert c32_start == c31_v8

def test_ancestor_line_intact():
    """Verify ancestral chain (Stage 26 through Stage 31) remains unbroken."""
    ancestors = [
        "stage-31-complete-v8^{commit}",
        "stage-30-complete-v3^{commit}",
        "stage-29-complete-v2^{commit}",
        "stage-28a-complete-v4^{commit}",
        "stage-27-infrastructure-complete-v3^{commit}",
        "stage-26-complete-v5^{commit}"
    ]
    for tag_ref in ancestors:
        assert git_is_ancestor(tag_ref, "stage-32-start^{commit}"), f"{tag_ref} is not an ancestor of stage-32-start"

def test_candidate_lexicon_entry_schema_defaults():
    """Verify CandidateLexiconEntry defaults obey governance state contracts."""
    entry = CandidateLexiconEntry(
        entry_id="SI-LEX-000001",
        canonical_form="ළමයා",
        grapheme_count=5,
        code_point_count=7,
        canonical_frequency=17,
        canonical_document_frequency=10,
        weighted_provenance_frequency=17.0,
        source_count=3,
        eligible_source_count=5,
        observed_source_count=3,
        source_dispersion=0.7821,
        rights_profile_refs=[
            RightsProfileReference(source_id="SRC-SI-001", rights_profile_id="RP-SRC-SI-001", rights_profile_version=1)
        ]
    )
    assert entry.validation_status == "draft"
    assert entry.expert_validated is False
    assert entry.approved_for_child_delivery is False
    assert entry.approved_for_unsupervised_child_delivery is False
    assert entry.requires_expert_review is True
    assert entry.provisional_band == ProvisionalVocabularyBand.REVIEW_REQUIRED

def test_token_occurrence_schema_validation():
    """Verify TokenOccurrenceRecord enforces protected:// refs and half-open code point intervals."""
    occ = TokenOccurrenceRecord(
        occurrence_id="SI-OCC-00000001",
        entry_id="SI-LEX-000001",
        canonical_record_id="SI-PILOT-000001",
        provenance_record_id="SI-PILOT-000001",
        source_id="SRC-SI-001",
        split_group_id="SPLIT-GRP-SI-000001",
        token_index=3,
        normalized_start_code_point=14,
        normalized_end_code_point=19,
        context_storage_ref="protected://sinhala_lexicon/contexts/SI-OCC-00000001.json",
        token_text_storage_ref="protected://sinhala_lexicon/tokens/SI-OCC-00000001.txt",
        rights_profile_id="RP-SRC-SI-001",
        rights_profile_version=1,
        stage30_configuration_hash="hash30",
        stage31_configuration_hash="hash31",
        corpus_artifact_sha256="corpus_hash",
        occurrence_disposition=OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE
    )
    assert occ.surface_form_hmac is None
    assert occ.hmac_domain == "sinhala-lexicon-surface-form"
    assert occ.offset_interval == "zero_based_half_open"

    # Reject non-protected URI
    with pytest.raises(ValidationError):
        TokenOccurrenceRecord.model_validate({
            **occ.model_dump(),
            "context_storage_ref": "/local/path/context.json"
        })

    # Reject reversed code point interval
    with pytest.raises(ValidationError):
        TokenOccurrenceRecord(
            occurrence_id="SI-OCC-00000002",
            entry_id="SI-LEX-000001",
            canonical_record_id="SI-PILOT-000001",
            provenance_record_id="SI-PILOT-000001",
            source_id="SRC-SI-001",
            split_group_id="SPLIT-GRP-SI-000001",
            token_index=0,
            normalized_start_code_point=25,
            normalized_end_code_point=10,  # invalid
            context_storage_ref="protected://ctx.json",
            token_text_storage_ref="protected://tok.txt",
            rights_profile_id="RP-1",
            rights_profile_version=1,
            stage30_configuration_hash="h30",
            stage31_configuration_hash="h31",
            corpus_artifact_sha256="chash",
            occurrence_disposition=OccurrenceDisposition.INCLUDED_CANDIDATE_OCCURRENCE
        )

def test_expert_review_validator_blocks_unauthorized_completion():
    """Verify LexiconExpertReviewRecord prevents setting reviewed_at without reviewer_id or without decision."""
    # Setting reviewed_at without reviewer_id must fail
    with pytest.raises(ValidationError, match="reviewed_at cannot be populated when reviewer_id is null"):
        LexiconExpertReviewRecord(
            entry_id="SI-LEX-000001",
            reviewed_at="2026-10-16T10:00:00Z"
        )

    # Setting reviewed_at with reviewer_id but without any decision must fail
    with pytest.raises(ValidationError, match="reviewed_at cannot be populated when all review decisions are NOT_REVIEWED"):
        LexiconExpertReviewRecord(
            entry_id="SI-LEX-000001",
            reviewer_id="REV-EXP-01",
            reviewed_at="2026-10-16T10:00:00Z"
        )

    # Valid completed review record
    valid_review = LexiconExpertReviewRecord(
        entry_id="SI-LEX-000001",
        reviewer_id="REV-EXP-01",
        lemma_decision=ReviewDecision.ACCEPT,
        age_band_decision=AgeBandReviewDecision.FOUNDATIONAL,
        reviewed_at="2026-10-16T10:00:00Z"
    )
    assert valid_review.reviewer_id == "REV-EXP-01"
    assert valid_review.lemma_decision == ReviewDecision.ACCEPT

def test_occurrence_vs_entry_disposition_separation():
    """Verify occurrence and entry dispositions are separate contracts."""
    occ_set = set(e.value for e in OccurrenceDisposition)
    entry_set = set(e.value for e in TerminalEntryDisposition)
    assert "INCLUDED_CANDIDATE_OCCURRENCE" in occ_set
    assert "INCLUDED_CANDIDATE_OCCURRENCE" not in entry_set
    assert "ACCEPTED_DRAFT_LEXICON_ENTRY" in entry_set
    assert "ACCEPTED_DRAFT_LEXICON_ENTRY" not in occ_set
