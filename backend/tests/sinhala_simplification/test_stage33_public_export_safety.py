"""
Stage 33 — Unit Tests for Public Export Safety.
Verifies that public export serialization contains strictly zero literal or reconstructable Sinhala text.
"""

import pytest
from app.sinhala_simplification.enums import CorpusView, FinalDisposition
from app.sinhala_simplification.schemas import FinalRewriteRecord
from app.sinhala_simplification.serialization import to_public_rewrite_record


def test_public_rewrite_record_has_no_text():
    rec = FinalRewriteRecord(
        output_id="SI-SIMP-OUT-000001",
        request_id="SI-SIMP-REQ-000001",
        selected_candidate_id="SI-CAND-000001",
        final_disposition=FinalDisposition.DRAFT_REWRITE_SELECTED,
        output_storage_ref="protected://sinhala_simplification/outputs/SI-SIMP-OUT-000001.txt",
        output_sha256_internal="a" * 64,
        applied_rule_ids=["SI-LEX-SUB-0001"],
        guard_results={},
        language="si",
        locale="si-LK",
        script="Sinh",
        validation_status="draft",
        expert_validated=False,
        research_eligible=False,
        approved_for_child_delivery=False,
        approved_for_unsupervised_child_delivery=False,
        requires_expert_review=True,
        corpus_view=CorpusView.CANONICAL_ANALYTICAL_150,
        rights_profile_refs=["SRC-SI-001-RP-01"]
    )

    pub_dict = to_public_rewrite_record(rec)
    assert "source_text" not in pub_dict
    assert "output_text" not in pub_dict
    assert "candidate_text_internal" not in pub_dict
    assert pub_dict["validation_status"] == "draft"
    assert pub_dict["approved_for_child_delivery"] is False
