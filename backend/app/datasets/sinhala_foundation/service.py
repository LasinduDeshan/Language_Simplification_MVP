"""
Service layer for Sinhala Foundation Unicode verification and DTO operations.
"""
from typing import List, Optional, Tuple, Dict, Any
from .repository import SinhalaFoundationRepository
from .schemas import LocalizedContentRecord, SinhalaTechnicalFixture
from app.localization.unicode_guards import verify_code_point_equality, has_replacement_character, extract_code_points

class SinhalaFoundationService:
    def __init__(self, repository: Optional[SinhalaFoundationRepository] = None):
        self.repository = repository or SinhalaFoundationRepository()

    def store_and_verify_round_trip(self, record: LocalizedContentRecord) -> Tuple[bool, LocalizedContentRecord, Dict[str, Any]]:
        """
        Store record in database, read back, and verify exact code-point equality.
        """
        self.repository.save_record(record)
        retrieved = self.repository.get_record(record.content_id)
        if not retrieved:
            return False, record, {"error": "Record not found after save"}

        code_points_match, in_cps, out_cps = verify_code_point_equality(record.text_value, retrieved.text_value)
        replacement_detected = has_replacement_character(retrieved.text_value)

        verification_details = {
            "code_points_match": code_points_match,
            "input_code_points": in_cps,
            "retrieved_code_points": out_cps,
            "replacement_character_detected": replacement_detected,
            "exact_text_match": record.text_value == retrieved.text_value
        }

        success = code_points_match and not replacement_detected and verification_details["exact_text_match"]
        return success, retrieved, verification_details

    def execute_fixture_round_trip(self, fixture: SinhalaTechnicalFixture) -> Dict[str, Any]:
        """
        Execute round-trip check on a technical fixture without persistence side-effects.
        """
        cps = extract_code_points(fixture.input_text)
        matches = (cps == fixture.expected_code_points)
        rep = has_replacement_character(fixture.input_text)
        return {
            "fixture_id": fixture.fixture_id,
            "category": fixture.category,
            "matches_expected": matches,
            "replacement_detected": rep,
            "code_points": cps,
            "status": "PASSED" if matches and not rep else "FAILED"
        }
