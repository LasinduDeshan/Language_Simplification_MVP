"""
Stage 21 NLP Preprocessing Package
Component 3: AI/NLP-Based Language Simplification
"""
from app.nlp_preprocessing.version import PIPELINE_VERSION, SCHEMA_VERSION, MODEL_METADATA
from app.nlp_preprocessing.config import PreprocessingConfig
from app.nlp_preprocessing.schemas import (
    DatasetSplit,
    TextInstance,
    TokenRecord,
    SentenceRecord,
    SurfaceFeatures,
    LexicalFeatures,
    SyntacticFeatures,
    ProtectedMeaningFeatures,
    LinguisticFeatureSet,
    LanguageVerificationRecord,
    PreprocessedRecord
)

__all__ = [
    "PIPELINE_VERSION",
    "SCHEMA_VERSION",
    "MODEL_METADATA",
    "PreprocessingConfig",
    "DatasetSplit",
    "TextInstance",
    "TokenRecord",
    "SentenceRecord",
    "SurfaceFeatures",
    "LexicalFeatures",
    "SyntacticFeatures",
    "ProtectedMeaningFeatures",
    "LinguisticFeatureSet",
    "LanguageVerificationRecord",
    "PreprocessedRecord"
]
