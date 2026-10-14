"""
Schemas for Sinhala Foundation technical fixtures and persistence records.
"""
from typing import Literal, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class SinhalaTechnicalFixture(BaseModel):
    """
    Governed technical fixture structure.
    Strictly marked with approved_for_child_delivery=False.
    """
    model_config = ConfigDict(extra="forbid")
    fixture_id: str
    category: str
    input_text: str
    expected_code_points: List[str]
    source_type: str = "technical_fixture"
    validation_status: str = "draft"
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True
    intended_test: str

class LocalizedContentRecord(BaseModel):
    """
    Language-tagged content record for persistence and API round trips.
    """
    model_config = ConfigDict(extra="forbid")
    content_id: str
    language: Literal["en", "si"]
    locale: Literal["en-LK", "si-LK"]
    text_role: str
    text_value: str
    source_type: str = "technical_fixture"
    validation_status: str = "draft"
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True
