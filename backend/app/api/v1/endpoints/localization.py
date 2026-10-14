"""
FastAPI endpoints for Stage 29 localization, locale negotiation, and Unicode round trips.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse

from app.localization.schemas import (
    LocaleSelectionRequest,
    ResolvedLocaleResponse,
    LocalizedContentDTO,
    UnicodeRoundTripProbeRequest,
    UnicodeRoundTripProbeResponse
)
from app.localization.locale_registry import (
    resolve_locale,
    LOCALE_METADATA,
    DEFAULT_LOCALE
)
from app.localization.unicode_guards import (
    extract_code_points,
    has_replacement_character,
    verify_code_point_equality,
    count_grapheme_clusters
)
from app.localization.invisible_characters import (
    validate_field_controls,
    escape_controls_for_log
)
from app.localization.enums import FieldCategory
from app.datasets.sinhala_foundation.repository import SinhalaFoundationRepository
from app.datasets.sinhala_foundation.service import SinhalaFoundationService
from app.datasets.sinhala_foundation.schemas import LocalizedContentRecord
from app.datasets.sinhala_foundation.export_service import SinhalaExportService

router = APIRouter(prefix="/localization", tags=["localization"])
_repository = SinhalaFoundationRepository()
_service = SinhalaFoundationService(repository=_repository)

@router.get("/locales", response_model=Dict[str, Any])
def get_supported_locales():
    """
    Return all registered, supported locales and default fallback.
    """
    return {
        "default_locale": DEFAULT_LOCALE,
        "locales": LOCALE_METADATA
    }

@router.post("/locale", response_model=ResolvedLocaleResponse)
def select_locale(request: LocaleSelectionRequest):
    """
    Validate and resolve client locale request.
    Strictly derives script and direction on server. Extra fields are rejected (422).
    """
    resolved = resolve_locale(request.locale)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported locale '{request.locale}'."
        )
    return ResolvedLocaleResponse(**resolved)

@router.post("/probe/round-trip", response_model=UnicodeRoundTripProbeResponse)
def test_unicode_round_trip(probe: UnicodeRoundTripProbeRequest):
    """
    Verify exact decoded Unicode code-point preservation across API JSON boundary.
    """
    cps = extract_code_points(probe.payload)
    matches = (cps == probe.expected_code_points)
    replacement = has_replacement_character(probe.payload)
    status_str = "PASSED" if matches and not replacement else "FAILED"

    return UnicodeRoundTripProbeResponse(
        test_id=probe.test_id,
        payload=probe.payload,
        code_points=cps,
        matches_expected=matches,
        replacement_character_detected=replacement,
        status=status_str
    )

@router.post("/content", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def store_localized_content(content: LocalizedContentDTO):
    """
    Store localized content with field control validation and governance.
    """
    # Enforce control character policy
    valid, err, _ = validate_field_controls(content.text_value, FieldCategory.EDUCATIONAL_TEXT)
    if not valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err)

    record = LocalizedContentRecord(
        content_id=f"CNT-{content.locale}-{hash(content.text_value) % 10000000:07d}",
        language=content.language,
        locale=content.locale,
        text_role=content.text_role,
        text_value=content.text_value,
        source_type=content.source_type,
        validation_status=content.validation_status,
        research_eligible=content.research_eligible,
        approved_for_child_delivery=content.approved_for_child_delivery,
        requires_expert_review=content.requires_expert_review
    )

    success, saved, details = _service.store_and_verify_round_trip(record)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unicode persistence verification failed")

    return {
        "status": "success",
        "content_id": saved.content_id,
        "verification_details": details
    }

@router.get("/content/{content_id}", response_model=LocalizedContentDTO)
def get_localized_content(content_id: str):
    """
    Retrieve localized content by ID.
    """
    record = _repository.get_record(content_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Content {content_id} not found")

    return LocalizedContentDTO(
        text_role=record.text_role,
        text_value=record.text_value,
        language=record.language,
        locale=record.locale,
        source_type=record.source_type,
        validation_status=record.validation_status,
        research_eligible=record.research_eligible,
        approved_for_child_delivery=record.approved_for_child_delivery,
        requires_expert_review=record.requires_expert_review
    )

@router.get("/export/json")
def export_json(language: Optional[str] = "si"):
    """
    Export localized records as UTF-8 JSON.
    """
    records = _repository.list_records_by_language(language)
    raw_bytes, sha256_hash = SinhalaExportService.export_records_to_json(records)
    return Response(
        content=raw_bytes,
        media_type="application/json; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=sinhala_records_{language}.json",
            "X-Artifact-SHA256": sha256_hash
        }
    )

@router.get("/export/csv")
def export_csv(language: Optional[str] = "si", use_bom: bool = False):
    """
    Export localized records as UTF-8 CSV.
    """
    records = _repository.list_records_by_language(language)
    raw_bytes, sha256_hash = SinhalaExportService.export_records_to_csv(records, use_bom=use_bom)
    return Response(
        content=raw_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=sinhala_records_{language}.csv",
            "X-Artifact-SHA256": sha256_hash
        }
    )
