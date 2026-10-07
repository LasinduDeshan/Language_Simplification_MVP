"""
Stage 21 Preprocessing Configuration
"""
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class PreprocessingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    normalization_form: Literal["NFC", "NFKC"] = "NFC"
    allow_nfkc_diagnostic: bool = False
    language_confidence_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    primary_engine: Literal["spacy", "stanza"] = "spacy"
    enable_fallback: bool = True
    long_word_char_threshold: int = Field(default=7, ge=4)
    cache_enabled: bool = True
    max_batch_size: int = Field(default=50, ge=1)
    random_seed: int = 2026
    evaluation_run_id: Optional[str] = None
    allow_locked_test: bool = False
