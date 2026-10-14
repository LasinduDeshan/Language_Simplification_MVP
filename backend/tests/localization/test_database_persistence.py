"""
Database persistence tests for Sinhala content, ZWJ ligatures, and code-point fidelity.
"""
import pytest
import tempfile
from pathlib import Path
from app.datasets.sinhala_foundation.repository import SinhalaFoundationRepository
from app.datasets.sinhala_foundation.service import SinhalaFoundationService
from app.datasets.sinhala_foundation.schemas import LocalizedContentRecord

@pytest.fixture
def temp_repo():
    repo = SinhalaFoundationRepository(db_path=":memory:")
    yield repo
    repo.close()

def test_sinhala_persistence_round_trip(temp_repo):
    service = SinhalaFoundationService(repository=temp_repo)
    
    test_record = LocalizedContentRecord(
        content_id="REC-SI-001",
        language="si",
        locale="si-LK",
        text_role="instruction",
        text_value="පහත දැක්වෙන වචනය තෝරන්න (ශ්‍රී ලංකාව)",
        source_type="technical_fixture",
        validation_status="draft",
        research_eligible=False,
        approved_for_child_delivery=False,
        requires_expert_review=True
    )
    
    success, retrieved, details = service.store_and_verify_round_trip(test_record)
    assert success
    assert retrieved.text_value == test_record.text_value
    assert details["code_points_match"]
    assert not details["replacement_character_detected"]

def test_sinhala_combining_marks_and_zwj_persistence(temp_repo):
    service = SinhalaFoundationService(repository=temp_repo)
    
    # Complex ligatures: Bandi akuru, Yansaya, Rakaransaya
    test_record = LocalizedContentRecord(
        content_id="REC-SI-002",
        language="si",
        locale="si-LK",
        text_role="sample_text",
        text_value="ව්‍යවස්ථාදායක මණ්ඩලය සහ ක්‍ෂීරපායී සතුන්",
        source_type="technical_fixture",
        validation_status="draft"
    )
    
    success, retrieved, details = service.store_and_verify_round_trip(test_record)
    assert success
    assert details["code_points_match"]
    assert "\u200D" in retrieved.text_value  # ZWJ preserved

def test_delete_and_list_records(temp_repo):
    rec1 = LocalizedContentRecord(content_id="C1", language="si", locale="si-LK", text_role="title", text_value="සිංහල 1")
    rec2 = LocalizedContentRecord(content_id="C2", language="en", locale="en-LK", text_role="title", text_value="English 1")
    
    temp_repo.save_record(rec1)
    temp_repo.save_record(rec2)
    
    si_records = temp_repo.list_records_by_language("si")
    assert len(si_records) == 1
    assert si_records[0].content_id == "C1"
    
    assert temp_repo.delete_record("C1")
    assert temp_repo.get_record("C1") is None
