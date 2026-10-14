"""
Export service for Sinhala Foundation datasets: UTF-8 JSON and CSV with SHA-256 integrity.
"""
from typing import List, Dict, Any, Tuple
from pathlib import Path
from .schemas import LocalizedContentRecord
from app.localization.serialization import serialize_to_utf8_json, serialize_to_utf8_csv

class SinhalaExportService:
    @staticmethod
    def export_records_to_json(records: List[LocalizedContentRecord]) -> Tuple[bytes, str]:
        data = [r.model_dump() for r in records]
        return serialize_to_utf8_json(data)

    @staticmethod
    def export_records_to_csv(records: List[LocalizedContentRecord], use_bom: bool = False) -> Tuple[bytes, str]:
        rows = [r.model_dump() for r in records]
        fieldnames = [
            "content_id", "language", "locale", "text_role", "text_value",
            "source_type", "validation_status", "research_eligible",
            "approved_for_child_delivery", "requires_expert_review"
        ]
        return serialize_to_utf8_csv(rows, fieldnames=fieldnames, use_bom=use_bom)
