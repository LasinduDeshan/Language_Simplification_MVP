"""
Unit tests for WP9 Export Filtering, Rights Enforcement, and Governance Invariants.
"""

import pytest
from app.datasets.sinhala_external.export_service import build_public_export_record
from app.datasets.sinhala_external.schemas import (
    PilotCorpusRecord,
    CorpusSplit,
    SplitComponentType,
)

def create_sample_record(source_id: str, export_policy: str, redistributable: bool) -> PilotCorpusRecord:
    return PilotCorpusRecord(
        record_id="SI-PILOT-000001",
        document_id="DOC-SI-000001",
        source_id=source_id,
        all_contributing_sources=[source_id],
        retrieval_id="RET-SI-001-001",
        rights_profile_id=f"RP-{source_id}",
        rights_profile_version=1,
        public_record_digest="a"*64,
        hmac_key_id="HMAC-2026-V1",
        hmac_key_version=1,
        digest_input_schema="sinhala-pilot-record:v1",
        split=CorpusSplit.TRAIN,
        split_group_id="SPLIT-GRP-SI-000001",
        component_type=SplitComponentType.TRAIN_ONLY_DEVELOPMENT_COMPONENT,
        document_group_id="GRP-1",
        source_offset_or_locator="seq_idx:000001",
        provisional_domain="informational_provisional",
        authoring_origin="human_authored_claimed",
        is_method_development_record=True,
        stage30_disposition="PASSED",
        stage30_configuration_hash="b"*64,
        stage31_configuration_hash="c"*64,
        normalized_text_storage_ref="protected://sinhala_external/normalized/SI-PILOT-000001.txt",
        sentence_count=2,
        token_count=15,
        grapheme_count=80,
        quality_flags=[],
        effective_export_policy=export_policy,
        literal_text_redistributable=redistributable,
        canonical_record_id="SI-PILOT-000001",
        is_canonical_exact_record=True,
        exact_duplicate_weight=1.0,
        retention_reason="PRIMARY_CANONICAL_RECORD"
    )

def test_protected_internal_only_suppresses_literal_text():
    """Validates that SRC-SI-004 records with PROTECTED_INTERNAL_ONLY have literal text suppressed."""
    rec = create_sample_record(
        source_id="SRC-SI-004",
        export_policy="PROTECTED_INTERNAL_ONLY",
        redistributable=False
    )
    exported = build_public_export_record(rec, "මෙය විශ්වවිද්‍යාල පර්යේෂණ වාර්තාවකි.")
    assert exported is not None
    assert exported["text"] is None
    assert exported["export_redistribution_status"] == "LITERAL_TEXT_SUPPRESSED_PROTECTED_INTERNAL_ONLY"
    assert exported["public_record_digest"] == "a"*64

def test_indiccorp_licence_mismatch_suppression():
    """Validates that SRC-SI-002 records have literal text suppressed pending licence verification."""
    rec = create_sample_record(
        source_id="SRC-SI-002",
        export_policy="PUBLIC_PERMITTED_CC_BY",
        redistributable=True
    )
    exported = build_public_export_record(rec, "ඉන්දියානු භාෂා සඳහා වූ වාර්තාවකි.")
    assert exported is not None
    assert exported["text"] is None
    assert exported["export_redistribution_status"] == "REVIEW_REQUIRED_ARTIFACT_LICENCE_MISMATCH"

def test_public_permitted_includes_literal_text():
    """Validates that verified CC-BY or CC-BY-SA records include literal text."""
    rec = create_sample_record(
        source_id="SRC-SI-001",
        export_policy="PUBLIC_PERMITTED_CC_BY_SA",
        redistributable=True
    )
    exported = build_public_export_record(rec, "ශ්‍රී ලංකාවේ ඉතිහාසය අවුරුදු 2500කට වඩා පැරණිය.")
    assert exported is not None
    assert exported["text"] == "ශ්‍රී ලංකාවේ ඉතිහාසය අවුරුදු 2500කට වඩා පැරණිය."
    assert exported["export_redistribution_status"] == "PUBLIC_TEXT_PERMITTED_WITH_ATTRIBUTION"

def test_governance_child_delivery_invariants():
    """Validates that all export records strictly preserve draft child-delivery safeguards."""
    rec = create_sample_record(
        source_id="SRC-SI-008",
        export_policy="PUBLIC_PERMITTED_CC_BY",
        redistributable=True
    )
    exported = build_public_export_record(rec, "ළමා කතාවකි.")
    assert exported is not None
    gov = exported["governance_status"]
    assert gov["validation_status"] == "draft"
    assert gov["research_eligible"] is False
    assert gov["approved_for_child_delivery"] is False
    assert gov["requires_expert_review"] is True
