"""
Unit tests for Stage 20 Dynamic Version Calculation.
"""
import pytest

def calculate_next_version(current_dataset_version: str, current_schema_version: str, is_content_expansion: bool, is_schema_breaking: bool):
    if is_schema_breaking:
        major, minor, patch = map(int, current_schema_version.split("."))
        return current_dataset_version, f"{major + 1}.0.0"
    elif is_content_expansion:
        major, minor, patch = map(int, current_dataset_version.split("."))
        return f"{major}.{minor + 1}.0", current_schema_version
    else:
        major, minor, patch = map(int, current_dataset_version.split("."))
        return f"{major}.{minor}.{patch + 1}", current_schema_version

def test_version_calculation_expansion():
    # v0.1.0 with content expansion -> v0.2.0, schema unchanged
    d_ver, s_ver = calculate_next_version("0.1.0", "1.0.0", is_content_expansion=True, is_schema_breaking=False)
    assert d_ver == "0.2.0"
    assert s_ver == "1.0.0"

def test_version_calculation_schema_breaking():
    d_ver, s_ver = calculate_next_version("0.1.0", "1.0.0", is_content_expansion=True, is_schema_breaking=True)
    assert d_ver == "0.1.0"
    assert s_ver == "2.0.0"
