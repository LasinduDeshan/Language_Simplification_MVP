"""
Stage 33 — Unit Tests for Rights Inheritance & Protected Payload Isolation.
"""

import os
import pytest
from pathlib import Path
from app.sinhala_simplification.serialization import to_public_rule_record
from app.sinhala_simplification.storage import get_protected_storage_root, PROJECT_ROOT
from app.sinhala_simplification.rule_registry import RuleRegistry


def test_protected_storage_root_boundary():
    root = get_protected_storage_root()
    assert not root.is_relative_to(PROJECT_ROOT), "Protected storage root must NOT be inside project root"


def test_protected_storage_fail_closed_unset(monkeypatch):
    monkeypatch.delenv("SINHALA_SIMPLIFICATION_PROTECTED_ROOT", raising=False)
    with pytest.raises(RuntimeError, match="mandatory and unset"):
        get_protected_storage_root()


def test_protected_storage_fail_closed_inside_worktree(monkeypatch, tmp_path):
    inside_dir = PROJECT_ROOT / "test_scratch_protected"
    inside_dir.mkdir(parents=True, exist_ok=True)
    try:
        monkeypatch.setenv("SINHALA_SIMPLIFICATION_PROTECTED_ROOT", str(inside_dir))
        with pytest.raises(RuntimeError, match="must NOT resolve inside working tree"):
            get_protected_storage_root()
    finally:
        if inside_dir.exists():
            inside_dir.rmdir()


def test_public_rule_registry_has_no_raw_sinhala():
    registry = RuleRegistry()
    rules = registry.load_registry()
    for rule in rules.values():
        pub_dict = to_public_rule_record(rule.metadata)
        # Verify no raw Sinhala characters in pattern ref
        assert not any(ord(c) >= 0x0D80 and ord(c) <= 0x0DFF for c in pub_dict["source_pattern_ref"])
        assert not any(ord(c) >= 0x0D80 and ord(c) <= 0x0DFF for c in pub_dict["target_template_ref"])
        # Verify structured rights profile format
        assert len(pub_dict["rights_profile_refs"]) > 0
        for r_ref in pub_dict["rights_profile_refs"]:
            assert r_ref["rights_profile_id"].startswith("RP-SRC-SI-")
            assert "rights_profile_version" in r_ref
