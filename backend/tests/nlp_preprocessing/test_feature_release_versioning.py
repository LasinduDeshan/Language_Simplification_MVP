"""
Unit tests for Feature Release Versioning & Constants
"""
from app.nlp_preprocessing.version import (
    PIPELINE_VERSION,
    SCHEMA_VERSION,
    SOURCE_DATASET_VERSION,
    MODEL_METADATA
)
from app.nlp_preprocessing.config import PreprocessingConfig

def test_feature_release_constants():
    assert PIPELINE_VERSION == "1.0.0"
    assert SCHEMA_VERSION == "1.0.0"
    assert SOURCE_DATASET_VERSION == "0.2.0"
    assert MODEL_METADATA["spacy_model_name"] == "en_core_web_sm"

def test_config_version_alignment():
    config = PreprocessingConfig()
    assert config.normalization_form == "NFC"
    assert config.allow_nfkc_diagnostic is False
    assert config.allow_locked_test is False
