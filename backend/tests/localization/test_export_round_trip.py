"""
Tests for UTF-8 JSON and CSV export byte integrity and SHA-256 reproducibility.
"""
import json
import csv
import io
import hashlib
from app.datasets.sinhala_foundation.schemas import LocalizedContentRecord
from app.datasets.sinhala_foundation.export_service import SinhalaExportService
from app.localization.serialization import verify_export_bytes

def test_json_export_utf8_integrity():
    records = [
        LocalizedContentRecord(
            content_id="EXP-001",
            language="si",
            locale="si-LK",
            text_role="instruction",
            text_value="පහත රූපය බලන්න"
        ),
        LocalizedContentRecord(
            content_id="EXP-002",
            language="si",
            locale="si-LK",
            text_role="feedback",
            text_value="ඉතා හොඳයි!"
        )
    ]

    raw_bytes, sha256_hash = SinhalaExportService.export_records_to_json(records)

    # 1. Byte-level hash check
    valid_hash, computed_hash = verify_export_bytes(raw_bytes, sha256_hash)
    assert valid_hash

    # 2. Decode bytes as UTF-8
    decoded_str = raw_bytes.decode("utf-8")
    assert "පහත රූපය බලන්න" in decoded_str
    assert "ඉතා හොඳයි!" in decoded_str

    # 3. Parse back to json and verify fields
    parsed = json.loads(decoded_str)
    assert len(parsed) == 2
    assert parsed[0]["content_id"] == "EXP-001"
    assert parsed[0]["text_value"] == "පහත රූපය බලන්න"

def test_csv_export_utf8_integrity():
    records = [
        LocalizedContentRecord(
            content_id="CSV-001",
            language="si",
            locale="si-LK",
            text_role="label",
            text_value="ආරම්භ කරන්න"
        )
    ]

    raw_bytes, sha256_hash = SinhalaExportService.export_records_to_csv(records, use_bom=True)
    assert raw_bytes.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM

    valid_hash, _ = verify_export_bytes(raw_bytes, sha256_hash)
    assert valid_hash

    decoded_csv = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded_csv))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["text_value"] == "ආරම්භ කරන්න"
