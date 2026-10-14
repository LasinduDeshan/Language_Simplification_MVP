"""
Localization package for Stage 29: Sinhala Database, UI and Font Support.
"""
from .enums import (
    SupportedLanguage,
    SupportedLocale,
    ScriptCode,
    TextDirection,
    FieldCategory
)
from .schemas import (
    LocaleSelectionRequest,
    ResolvedLocaleResponse,
    LocalizedContentDTO,
    UnicodeRoundTripProbeRequest,
    UnicodeRoundTripProbeResponse
)
from .locale_registry import (
    resolve_locale,
    is_supported_locale,
    get_default_locale_metadata,
    DEFAULT_LOCALE,
    LOCALE_METADATA
)
from .invisible_characters import (
    validate_field_controls,
    escape_controls_for_log,
    DENYLISTED_CHARS
)
from .unicode_guards import (
    extract_code_points,
    verify_code_point_equality,
    has_replacement_character,
    count_grapheme_clusters,
    validate_grapheme_length
)
from .serialization import (
    serialize_to_utf8_json,
    serialize_to_utf8_csv,
    verify_export_bytes
)

__all__ = [
    "SupportedLanguage",
    "SupportedLocale",
    "ScriptCode",
    "TextDirection",
    "FieldCategory",
    "LocaleSelectionRequest",
    "ResolvedLocaleResponse",
    "LocalizedContentDTO",
    "UnicodeRoundTripProbeRequest",
    "UnicodeRoundTripProbeResponse",
    "resolve_locale",
    "is_supported_locale",
    "get_default_locale_metadata",
    "DEFAULT_LOCALE",
    "LOCALE_METADATA",
    "validate_field_controls",
    "escape_controls_for_log",
    "DENYLISTED_CHARS",
    "extract_code_points",
    "verify_code_point_equality",
    "has_replacement_character",
    "count_grapheme_clusters",
    "validate_grapheme_length",
    "serialize_to_utf8_json",
    "serialize_to_utf8_csv",
    "verify_export_bytes"
]
