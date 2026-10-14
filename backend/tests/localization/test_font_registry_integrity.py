"""
Tests for font registry integrity, license hashes, and binary verification.
"""
import json
import hashlib
from pathlib import Path

def test_font_registry_and_binary_integrity():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    registry_path = repo_root / "data" / "sinhala_foundation" / "registry" / "font_registry.json"
    assert registry_path.exists(), "font_registry.json must exist"

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    assert "fonts" in data
    assert len(data["fonts"]) >= 1

    entry = data["fonts"][0]
    assert entry["font_family"] == "Noto Sans Sinhala"
    assert entry["licence_identifier"] == "OFL-1.1"
    assert entry["redistribution_allowed"] is True

    # Verify font binary existence and SHA-256
    font_file = repo_root / entry["local_path"]
    assert font_file.exists(), f"Font file {font_file} must exist"
    actual_font_sha = hashlib.sha256(font_file.read_bytes()).hexdigest()
    assert actual_font_sha == entry["font_binary_sha256"]

    # Verify license file existence and SHA-256
    lic_file = repo_root / entry["licence_local_path"]
    assert lic_file.exists(), f"License file {lic_file} must exist"
    actual_lic_sha = hashlib.sha256(lic_file.read_bytes()).hexdigest()
    assert actual_lic_sha == entry["licence_file_sha256"]
