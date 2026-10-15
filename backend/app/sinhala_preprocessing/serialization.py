"""
Serialization module for Stage 30 Sinhala Preprocessing.
Provides canonical JSON export and import for SinhalaPreprocessingRecord.
"""

import json
from typing import Any, Dict
from app.sinhala_preprocessing.schemas import SinhalaPreprocessingRecord

def record_to_dict(record: SinhalaPreprocessingRecord) -> Dict[str, Any]:
    return record.model_dump(mode="json")

def record_to_json(record: SinhalaPreprocessingRecord, indent: int = 2) -> str:
    return json.dumps(record_to_dict(record), indent=indent, ensure_ascii=False)

def record_from_dict(data: Dict[str, Any]) -> SinhalaPreprocessingRecord:
    return SinhalaPreprocessingRecord.model_validate(data)

def record_from_json(json_str: str) -> SinhalaPreprocessingRecord:
    data = json.loads(json_str)
    return record_from_dict(data)
