"""
Central trusted locale registry for Stage 29.
Derives script and direction server-side to prevent client tampering.
"""
from typing import Dict, Any, Optional
from .enums import SupportedLanguage, SupportedLocale, ScriptCode, TextDirection

LOCALE_METADATA: Dict[str, Dict[str, Any]] = {
    "si-LK": {
        "language": SupportedLanguage.SI,
        "locale": SupportedLocale.SI_LK,
        "script": ScriptCode.SINH,
        "direction": TextDirection.LTR,
        "display_name_native": "සිංහල",
        "display_name_en": "Sinhala (Sri Lanka)",
        "is_active": True
    },
    "en-LK": {
        "language": SupportedLanguage.EN,
        "locale": SupportedLocale.EN_LK,
        "script": ScriptCode.LATN,
        "direction": TextDirection.LTR,
        "display_name_native": "English",
        "display_name_en": "English (Sri Lanka)",
        "is_active": True
    }
}

LOCALE_ALIASES: Dict[str, str] = {
    "en": "en-LK",
    "si": "si-LK"
}

DEFAULT_LOCALE = "en-LK"

def resolve_locale(requested_locale: str) -> Optional[Dict[str, Any]]:
    """
    Resolve requested locale or alias to canonical metadata dictionary.
    Returns None if unsupported.
    """
    if not requested_locale:
        return None
    canonical_key = LOCALE_ALIASES.get(requested_locale, requested_locale)
    return LOCALE_METADATA.get(canonical_key)

def is_supported_locale(requested_locale: str) -> bool:
    return resolve_locale(requested_locale) is not None

def get_default_locale_metadata() -> Dict[str, Any]:
    return LOCALE_METADATA[DEFAULT_LOCALE]
