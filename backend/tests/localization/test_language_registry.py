"""
Unit tests for central language and locale registry.
"""
import pytest
from app.localization.locale_registry import (
    resolve_locale,
    is_supported_locale,
    get_default_locale_metadata,
    DEFAULT_LOCALE
)
from app.localization.enums import SupportedLanguage, SupportedLocale, ScriptCode, TextDirection

def test_resolve_canonical_locales():
    si = resolve_locale("si-LK")
    assert si is not None
    assert si["language"] == SupportedLanguage.SI
    assert si["locale"] == SupportedLocale.SI_LK
    assert si["script"] == ScriptCode.SINH
    assert si["direction"] == TextDirection.LTR
    assert si["display_name_native"] == "සිංහල"

    en = resolve_locale("en-LK")
    assert en is not None
    assert en["language"] == SupportedLanguage.EN
    assert en["locale"] == SupportedLocale.EN_LK
    assert en["script"] == ScriptCode.LATN
    assert en["direction"] == TextDirection.LTR

def test_resolve_locale_aliases():
    assert resolve_locale("si") == resolve_locale("si-LK")
    assert resolve_locale("en") == resolve_locale("en-LK")

def test_unsupported_locales_rejected():
    assert resolve_locale("fr-FR") is None
    assert resolve_locale("SIN") is None
    assert resolve_locale("sinhala") is None
    assert resolve_locale("lk-si") is None
    assert resolve_locale("") is None
    assert not is_supported_locale("de-DE")

def test_default_fallback_locale():
    default_meta = get_default_locale_metadata()
    assert default_meta["locale"] == SupportedLocale.EN_LK
    assert DEFAULT_LOCALE == "en-LK"
