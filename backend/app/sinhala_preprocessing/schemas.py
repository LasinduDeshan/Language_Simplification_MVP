"""
Pydantic v2 Schemas for Stage 30 Sinhala Unicode Normalization and Preprocessing.
Enforces immutable raw capture, derived normalized representation, zero-based
half-open offset intervals [start, end), audit traces, and governance flags.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class MappingStatus(str, Enum):
    ONE_TO_ONE = "one_to_one"
    MANY_TO_ONE = "many_to_one"
    ONE_TO_MANY = "one_to_many"
    REORDERED = "reordered"
    NON_LOCAL = "non_local"
    UNMAPPED = "unmapped"

class TokenType(str, Enum):
    SINHALA_WORD = "SINHALA_WORD"
    LATIN_WORD = "LATIN_WORD"
    MIXED_SCRIPT_TOKEN = "MIXED_SCRIPT_TOKEN"
    ARABIC_NUMBER = "ARABIC_NUMBER"
    SINHALA_NUMBER = "SINHALA_NUMBER"
    PUNCTUATION = "PUNCTUATION"
    SYMBOL = "SYMBOL"
    UNKNOWN = "UNKNOWN"

class QualityFlag(str, Enum):
    NORMALIZATION_CHANGED = "NORMALIZATION_CHANGED"
    MIXED_SCRIPT_PRESENT = "MIXED_SCRIPT_PRESENT"
    JOINER_PRESENT = "JOINER_PRESENT"
    UNEXPECTED_JOINER_CONTEXT = "UNEXPECTED_JOINER_CONTEXT"
    PROHIBITED_CONTROL_PRESENT = "PROHIBITED_CONTROL_PRESENT"
    REPLACEMENT_CHARACTER_PRESENT = "REPLACEMENT_CHARACTER_PRESENT"
    UNSUPPORTED_SCRIPT_PRESENT = "UNSUPPORTED_SCRIPT_PRESENT"
    COMBINING_SEQUENCE_REVIEW = "COMBINING_SEQUENCE_REVIEW"
    EMPTY_AFTER_DERIVED_WHITESPACE = "EMPTY_AFTER_DERIVED_WHITESPACE"
    TOKENIZATION_UNCERTAIN = "TOKENIZATION_UNCERTAIN"
    SENTENCE_BOUNDARY_UNCERTAIN = "SENTENCE_BOUNDARY_UNCERTAIN"

class TerminalDisposition(str, Enum):
    REJECTED_INVALID_UNICODE = "REJECTED_INVALID_UNICODE"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    EXCLUDED_NON_SINHALA = "EXCLUDED_NON_SINHALA"
    PASSED_WITH_NORMALIZATION = "PASSED_WITH_NORMALIZATION"
    PASSED = "PASSED"

class HalfOpenSpan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start_code_point: int = Field(..., ge=0, description="Inclusive start index in Unicode code points")
    end_code_point: int = Field(..., ge=0, description="Exclusive end index in Unicode code points")

class OperationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str
    operation_type: str
    raw_spans: List[HalfOpenSpan] = Field(default_factory=list)
    normalized_spans: List[HalfOpenSpan] = Field(default_factory=list)
    before_sha256: str
    after_sha256: str
    changed: bool
    mapping_status: MappingStatus
    mapping_exact: bool
    rule_version: str

class SentenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sentence_index: int = Field(..., ge=0)
    text: str
    start_code_point: int = Field(..., ge=0)
    end_code_point: int = Field(..., ge=0)
    boundary_rule: str
    sha256: str

class TokenRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token_index: int = Field(..., ge=0)
    surface: str
    normalized: str
    token_type: TokenType
    start_code_point: int = Field(..., ge=0)
    end_code_point: int = Field(..., ge=0)
    grapheme_count: int = Field(..., ge=0)
    script_profile: Dict[str, float] = Field(default_factory=dict)

class PreprocessingFeatures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_utf8_byte_count: int = Field(..., ge=0)
    raw_code_point_count: int = Field(..., ge=0)
    raw_grapheme_count: int = Field(..., ge=0)
    normalized_utf8_byte_count: int = Field(..., ge=0)
    normalized_code_point_count: int = Field(..., ge=0)
    normalized_grapheme_count: int = Field(..., ge=0)
    sentence_count: int = Field(..., ge=0)
    token_count: int = Field(..., ge=0)
    sinhala_token_count: int = Field(..., ge=0)
    latin_token_count: int = Field(..., ge=0)
    mixed_script_token_count: int = Field(..., ge=0)
    numeric_token_count: int = Field(..., ge=0)
    punctuation_token_count: int = Field(..., ge=0)
    mean_graphemes_per_token: float = Field(..., ge=0.0)
    mean_tokens_per_sentence: float = Field(..., ge=0.0)
    max_token_grapheme_length: int = Field(..., ge=0)
    normalization_operation_count: int = Field(..., ge=0)
    whitespace_operation_count: int = Field(..., ge=0)

class SinhalaPreprocessingRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_id: str
    language: str = "si"
    locale: str = "si-LK"
    script: str = "Sinh"
    text_role: str = "prose"
    raw_text: str
    raw_text_sha256: str
    raw_utf8_byte_count: int = Field(..., ge=0)
    raw_code_point_count: int = Field(..., ge=0)
    raw_grapheme_count: int = Field(..., ge=0)
    normalized_text: str
    normalized_text_sha256: str
    normalized_utf8_byte_count: int = Field(..., ge=0)
    normalized_code_point_count: int = Field(..., ge=0)
    normalized_grapheme_count: int = Field(..., ge=0)
    normalization_form: str = "NFC"
    normalization_changed: bool = False
    operations: List[OperationRecord] = Field(default_factory=list)
    sentences: List[SentenceRecord] = Field(default_factory=list)
    tokens: List[TokenRecord] = Field(default_factory=list)
    features: PreprocessingFeatures
    quality_flags: List[QualityFlag] = Field(default_factory=list)
    final_disposition: TerminalDisposition
    disposition_reason_code: Optional[str] = None
    configuration_version: str
    configuration_sha256: str
    validation_status: str = "draft"
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    requires_expert_review: bool = True
