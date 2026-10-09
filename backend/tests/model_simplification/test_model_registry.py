"""
Unit tests for Stage 26 Model Registry and Metadata Tracking.
"""
import pytest
from pathlib import Path
from app.model_simplification.registry import ModelRegistry, ModelMetadata


def test_model_registry_default_models():
    reg = ModelRegistry()
    models = reg.list_models()
    model_ids = {m.model_id for m in models}

    assert "gemini-3.5-flash-lite-prompted" in model_ids
    assert "mt5-base-zero-shot" in model_ids
    assert "mbart-large-50-zero-shot" in model_ids
    assert "stage25-controlled-deterministic" in model_ids
    assert "hybrid-gemini-stage25-validated" in model_ids


def test_model_config_hash_consistency():
    reg = ModelRegistry()
    m = reg.get("gemini-3.5-flash-lite-prompted")
    assert m is not None
    assert m.config_hash is not None
    assert len(m.config_hash) == 64  # sha256 hex length


def test_stage25_comparator_hash_immutability():
    reg = ModelRegistry()
    s25 = reg.get("stage25-controlled-deterministic")
    assert s25 is not None
    assert s25.commit_revision == "6b785502b860d4e93d2d31b86bd653c33a210ac9"
    assert s25.intended_mode == "deterministic_stage25"


def test_model_registry_csv_export(tmp_path):
    reg = ModelRegistry()
    csv_file = tmp_path / "stage26_model_registry.csv"
    reg.export_csv(csv_file)

    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8")
    assert "gemini-3.5-flash-lite-prompted" in content
    assert "stage25-controlled-deterministic" in content
