"""
Stage 33 — End-to-End Pipeline Integration Tests.
"""

import pytest
from app.sinhala_simplification.enums import CorpusView, FinalDisposition, Partition
from app.sinhala_simplification.pipeline import SimplificationPipeline
from app.sinhala_simplification.schemas import RewriteRequest, RightsProfileBinding


def test_end_to_end_pipeline_draft_rewrite():
    pipeline = SimplificationPipeline()
    pipeline.initialize()

    request = RewriteRequest(
        request_id="REQ-E2E-001",
        record_id="REC-001",
        source_storage_ref="protected://test/REC-001.txt",
        source_sha256_internal="a" * 64,
        language="si",
        stage30_configuration_hash="b" * 64,
        stage31_split_manifest_hash="c" * 64,
        stage31_corpus_view=CorpusView.CANONICAL_ANALYTICAL_150,
        stage32_configuration_hash="d" * 64,
        stage32_lexicon_manifest_hash="e" * 64,
        stage33_configuration_hash="f" * 64,
        rights_profile_ids_and_versions=[RightsProfileBinding(rights_profile_id="SRC-SI-001-RP-01", version=1)],
        partition=Partition.TRAIN
    )

    # Input with rule match (පිළිබඳව -> ගැන)
    source_text = "මෙම පරිසරය පිළිබඳව අපි ඉගෙන ගනිමු."
    final_record, attempts, candidates, operations = pipeline.process_request(request, source_text)

    assert final_record.final_disposition == FinalDisposition.DRAFT_REWRITE_SELECTED
    assert final_record.selected_candidate_id is not None
    assert final_record.validation_status == "draft"
    assert final_record.expert_validated is False
    assert final_record.approved_for_child_delivery is False
    assert final_record.requires_expert_review is True
    assert len(final_record.applied_rule_ids) == 1
    assert "SI-LEX-SUB-0001" in final_record.applied_rule_ids
    assert len(operations) > 0


def test_end_to_end_pipeline_unchanged_fallback():
    pipeline = SimplificationPipeline()
    pipeline.initialize()

    request = RewriteRequest(
        request_id="REQ-E2E-002",
        record_id="REC-002",
        source_storage_ref="protected://test/REC-002.txt",
        source_sha256_internal="1" * 64,
        language="si",
        stage30_configuration_hash="2" * 64,
        stage31_split_manifest_hash="3" * 64,
        stage31_corpus_view=CorpusView.CANONICAL_ANALYTICAL_150,
        stage32_configuration_hash="4" * 64,
        stage32_lexicon_manifest_hash="5" * 64,
        stage33_configuration_hash="6" * 64,
        rights_profile_ids_and_versions=[RightsProfileBinding(rights_profile_id="SRC-SI-001-RP-01", version=1)],
        partition=Partition.TRAIN
    )

    # Input with no applicable rules
    source_text = "කුරුල්ලෝ අහසේ පියාඹති."
    final_record, attempts, candidates, operations = pipeline.process_request(request, source_text)

    assert final_record.final_disposition == FinalDisposition.UNCHANGED_NO_APPLICABLE_RULE
    assert final_record.selected_candidate_id is None
    assert final_record.validation_status == "draft"
    assert final_record.approved_for_child_delivery is False
