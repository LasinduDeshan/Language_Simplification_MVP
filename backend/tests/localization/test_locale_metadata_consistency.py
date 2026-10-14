"""
Unit tests for client metadata tampering protection and strict DTO validation.
"""
import pytest
from pydantic import ValidationError
from app.localization.schemas import LocaleSelectionRequest, ResolvedLocaleResponse
from app.localization.locale_registry import resolve_locale

def test_valid_locale_selection_request():
    req1 = LocaleSelectionRequest(locale="si-LK")
    assert req1.locale == "si-LK"

    req2 = LocaleSelectionRequest(locale="en-LK")
    assert req2.locale == "en-LK"

def test_reject_client_tampering_extra_fields():
    # Sending client-controlled script or direction must fail with ValidationError (translates to 422 in FastAPI)
    with pytest.raises(ValidationError):
        LocaleSelectionRequest(locale="si-LK", script="Latn")  # extra field forbidden!

    with pytest.raises(ValidationError):
        LocaleSelectionRequest(locale="si-LK", direction="rtl")

    with pytest.raises(ValidationError):
        LocaleSelectionRequest(locale="si-LK", language="en")

def test_reject_invalid_locale_values():
    with pytest.raises(ValidationError):
        LocaleSelectionRequest(locale="fr-FR")

    with pytest.raises(ValidationError):
        LocaleSelectionRequest(locale="SIN")

def test_resolved_locale_response_consistency():
    meta = resolve_locale("si-LK")
    resp = ResolvedLocaleResponse(**meta)
    assert resp.language == "si"
    assert resp.locale == "si-LK"
    assert resp.script == "Sinh"
    assert resp.direction == "ltr"
    assert resp.content_status == "draft"
