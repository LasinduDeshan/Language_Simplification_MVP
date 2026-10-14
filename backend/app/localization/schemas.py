"""
Pydantic DTOs for Stage 29 localization and client metadata security.
"""
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .enums import SupportedLanguage, SupportedLocale, ScriptCode, TextDirection

class LocaleSelectionRequest(BaseModel):
    """
    Client request DTO. Strictly forbids client-controlled script or direction injection.
    """
    model_config = ConfigDict(extra="forbid")
    locale: Literal["en-LK", "si-LK", "en", "si"]

class ResolvedLocaleResponse(BaseModel):
    """
    Server-resolved trusted locale metadata.
    """
    model_config = ConfigDict(extra="forbid")
    language: Literal["en", "si"]
    locale: Literal["en-LK", "si-LK"]
    script: Literal["Latn", "Sinh"]
    direction: Literal["ltr"]
    content_status: str = "draft"
    display_name_native: str
    display_name_en: str
    is_active: bool = True

class LocalizedContentDTO(BaseModel):
    """
    Localized content item carrying explicit language governance.
    """
    model_config = ConfigDict(extra="forbid")
    text_role: str
    text_value: str
    language: Literal["en", "si"]
    locale: Literal["en-LK", "si-LK"]
    source_type: str = "technical_fixture"
    validation_status: str = "draft"
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True

class UnicodeRoundTripProbeRequest(BaseModel):
    """
    DTO for testing Unicode round trips across API boundaries.
    """
    model_config = ConfigDict(extra="forbid")
    test_id: str
    payload: str
    expected_code_points: List[str]
    category: str = "technical_round_trip"

class UnicodeRoundTripProbeResponse(BaseModel):
    """
    DTO returning exact verified Unicode round-trip results.
    """
    model_config = ConfigDict(extra="forbid")
    test_id: str
    payload: str
    code_points: List[str]
    matches_expected: bool
    replacement_character_detected: bool
    status: str
