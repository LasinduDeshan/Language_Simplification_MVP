"""
Unit tests for Stage 31 schemas, duplicate-robots prevention, safe locators, and deterministic format parsers.
"""

import pytest
from pydantic import ValidationError
from pathlib import Path

from app.datasets.sinhala_external.schemas import (
    AcquisitionPolicy,
    RobotsTxtStatus,
    SourcePermissions,
    CandidateSourceRecord,
    PrimarySourceDecision,
    StagedDocumentRecord,
    ParsingStatus,
)
from app.datasets.sinhala_external.parsers.wikipedia_xml import WikipediaXmlParser
from app.datasets.sinhala_external.parsers.indiccorp_jsonl import IndicCorpJsonlParser
from app.datasets.sinhala_external.parsers.flores_tsv import FloresTsvParser
from app.datasets.sinhala_external.parsers.news_txt import NewsTxtParser
from app.datasets.sinhala_external.parsers.storyweaver_json import StoryWeaverJsonParser
from app.datasets.sinhala_external.parsers.dispatcher import DocumentStagingDispatcher
from app.datasets.sinhala_external.storage import ProtectedStorageManager

def test_source_permissions_forbids_duplicate_robots_txt_status():
    """Validates that SourcePermissions cannot accept robots_txt_status (forbids duplicate/conflicting fields)."""
    valid_perms = {
        "internal_research_use_allowed": True,
        "download_allowed": True,
        "local_storage_allowed": True,
        "modification_allowed": True,
        "derived_processing_allowed": True,
        "raw_redistribution_allowed": False,
        "derived_text_redistribution_allowed": False,
        "commercial_use_allowed": False,
        "attribution_required": True,
        "share_alike_required": False
    }
    # Clean permissions parse fine
    perms = SourcePermissions(**valid_perms)
    assert perms.internal_research_use_allowed is True

    # Attempting to inject robots_txt_status into permissions must raise ValidationError
    invalid_perms = dict(valid_perms)
    invalid_perms["robots_txt_status"] = "PERMITTED"
    with pytest.raises(ValidationError) as exc_info:
        SourcePermissions(**invalid_perms)
    assert "extra_forbidden" in str(exc_info.value)

def test_acquisition_policy_requires_valid_enum():
    """Validates that AcquisitionPolicy requires a valid RobotsTxtStatus enum value."""
    policy = AcquisitionPolicy(
        access_method="direct_download",
        robots_txt_status=RobotsTxtStatus.NOT_APPLICABLE
    )
    assert policy.robots_txt_status == RobotsTxtStatus.NOT_APPLICABLE

    with pytest.raises(ValidationError):
        AcquisitionPolicy(
            access_method="direct_download",
            robots_txt_status="INVALID_STATUS"
        )

def test_staged_document_rejects_unsafe_locators():
    """Enforces Invariant 6: source_offset_or_locator must reject host paths and query secrets."""
    valid_base = {
        "document_id": "DOC-SI-000001",
        "source_id": "SRC-SI-001",
        "retrieval_id": "RET-SI-001-001",
        "rights_profile_id": "RP-SRC-SI-001",
        "rights_profile_version": 1,
        "raw_file_sha256": "e8a12315aec2d0b448f3023f0eb6f182df9985c6ed82fb39b030ff21925fdf5f",
        "source_document_key": "page_1",
        "document_group_id": "GRP-WIKI-1",
        "source_offset_or_locator": "seq_idx:000001",
        "raw_text_storage_ref": "protected://sinhala_external/raw/SRC-SI-001/RET-SI-001-001/doc_001.txt"
    }

    # Safe locator passes
    doc = StagedDocumentRecord(**valid_base)
    assert doc.source_offset_or_locator == "seq_idx:000001"

    # Windows drive path is rejected
    unsafe_win = dict(valid_base)
    unsafe_win["source_offset_or_locator"] = "C:\\Users\\Secret\\doc.txt"
    with pytest.raises(ValidationError) as exc:
        StagedDocumentRecord(**unsafe_win)
    assert "leaks host path" in str(exc.value)

    # Linux / Unix user path is rejected
    unsafe_nix = dict(valid_base)
    unsafe_nix["source_offset_or_locator"] = "/home/developer/secret.json"
    with pytest.raises(ValidationError) as exc:
        StagedDocumentRecord(**unsafe_nix)
    assert "leaks host path" in str(exc.value)

    # Query secret is rejected
    unsafe_key = dict(valid_base)
    unsafe_key["source_offset_or_locator"] = "page_1?token=secret123"
    with pytest.raises(ValidationError) as exc:
        StagedDocumentRecord(**unsafe_key)
    assert "leaks host path" in str(exc.value)

def test_staged_document_requires_protected_storage_uri():
    """Enforces Invariant 12: raw_text_storage_ref must use abstract protected:// URI."""
    data = {
        "document_id": "DOC-SI-000001",
        "source_id": "SRC-SI-001",
        "retrieval_id": "RET-SI-001-001",
        "rights_profile_id": "RP-SRC-SI-001",
        "rights_profile_version": 1,
        "raw_file_sha256": "e8a12315aec2d0b448f3023f0eb6f182df9985c6ed82fb39b030ff21925fdf5f",
        "source_document_key": "page_1",
        "document_group_id": "GRP-WIKI-1",
        "source_offset_or_locator": "seq_idx:000001",
        "raw_text_storage_ref": "/var/data/raw/text.txt"
    }
    with pytest.raises(ValidationError) as exc:
        StagedDocumentRecord(**data)
    assert "protected://" in str(exc.value)

def test_wikipedia_xml_parser_technical_fixture():
    """Tests WikipediaXmlParser on format-specific technical XML fixture."""
    xml_fixture = """<?xml version="1.0" encoding="utf-8"?>
    <mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/">
      <page>
        <id>42</id>
        <title>ශ්‍රී ලංකාව</title>
        <revision>
          <text xml:space="preserve">
            <!-- Header comment -->
            {{Infobox Country}}
            == හැඳින්වීම ==
            ශ්‍රී ලංකාව [[ඉන්දියන් සාගරය|ඉන්දියන් සාගරයේ]] පිහිටි දූපත් රාජ්‍යයකි.&lt;ref&gt;මූලාශ්‍රය&lt;/ref&gt;
          </text>
        </revision>
      </page>
    </mediawiki>
    """.encode("utf-8")
    parser = WikipediaXmlParser()
    items = parser.parse(xml_fixture, "SRC-SI-001")
    assert len(items) == 1
    assert items[0].source_native_key == "wiki_page_42"
    assert "ශ්‍රී ලංකාව ඉන්දියන් සාගරයේ පිහිටි දූපත් රාජ්‍යයකි." in items[0].raw_text
    assert "Infobox" not in items[0].raw_text
    assert "<!--" not in items[0].raw_text

def test_indiccorp_jsonl_parser_technical_fixture():
    """Tests IndicCorpJsonlParser on format-specific JSONL fixture."""
    jsonl_fixture = b'{"id": "doc_1", "text": "\xe0\xb7\x81\xe0\xb7\x8a\xe2\x80\x8d\xe0\xb6\xbb\xe0\xb7\x93 \xe0\xb6\xbd\xe0\xb6\x82\xe0\xb6\x9a\xe0\xb7\x8f\xe0\xb7\x80 \xe0\xb6\x85\xe0\xb6\xb4\xe0\xb7\x9a \xe0\xb6\xbb\xe0\xb6\xa7\xe0\xb6\xba\xe0\xb7\x92."}\n{"id": "doc_2", "text": "   "}\n'
    parser = IndicCorpJsonlParser()
    items = parser.parse(jsonl_fixture, "SRC-SI-002")
    assert len(items) == 1
    assert items[0].source_native_key == "doc_1"
    assert "ශ්‍රී ලංකාව අපේ රටයි." in items[0].raw_text

def test_flores_tsv_parser_technical_fixture():
    """Tests FloresTsvParser on format-specific TSV fixture."""
    tsv_fixture = "sentence_id\ttext_sinhala\n101\tවිද්‍යාඥයන් විසින් සාගරය ගවේෂණය කරනු ලැබේ.\n".encode("utf-8")
    parser = FloresTsvParser()
    items = parser.parse(tsv_fixture, "SRC-SI-003")
    assert len(items) == 1
    assert items[0].source_native_key == "flores_101"
    assert "විද්‍යාඥයන් විසින් සාගරය ගවේෂණය කරනු ලැබේ." in items[0].raw_text

def test_metadata_only_source_is_strictly_blocked(tmp_path):
    """Enforces Invariant 22: METADATA_ONLY sources must never enter text parsing."""
    pred_file = tmp_path / "predeclaration.json"
    pred_file.write_text('{"sources": []}', encoding="utf-8")
    
    storage = ProtectedStorageManager(protected_root=tmp_path / "protected_root")
    dispatcher = DocumentStagingDispatcher(predeclaration_path=pred_file, storage=storage)

    with pytest.raises(PermissionError) as exc:
        dispatcher.parse_payload(
            source_id="SRC-SI-006",  # news.lk (METADATA_ONLY)
            retrieval_id="RET-SI-006-001",
            rights_profile_id="RP-SRC-SI-006",
            rights_profile_version=1,
            raw_file_sha256="abc",
            raw_bytes=b"dummy"
        )
    assert "METADATA_ONLY source SRC-SI-006 is barred" in str(exc.value)

def test_indiccorp_approved_source_schema_and_permissions():
    """Validates that SRC-SI-002 strictly conforms to the required governance schema:
    primary_decision == 'APPROVED' (valid PrimarySourceDecision enum)
    rights_scope == 'APPROVED_INTERNAL_NONCOMMERCIAL_ONLY'
    commercial_use_allowed == False
    public_literal_export_enabled == False
    """
    import json
    approved_path = Path(__file__).resolve().parents[4] / "data" / "sinhala_external" / "registry" / "approved_sources.json"
    data = json.loads(approved_path.read_text(encoding="utf-8"))
    src_si_002 = next((s for s in data["sources"] if s["source_id"] == "SRC-SI-002"), None)
    assert src_si_002 is not None
    assert src_si_002["primary_decision"] == PrimarySourceDecision.APPROVED.value
    assert src_si_002["rights_scope"] == "APPROVED_INTERNAL_NONCOMMERCIAL_ONLY"
    assert src_si_002["permissions"]["commercial_use_allowed"] is False
    assert src_si_002["permissions"]["public_literal_export_enabled"] is False

