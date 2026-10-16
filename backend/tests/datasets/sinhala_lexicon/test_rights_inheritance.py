"""
Tests for Version-Pinned Rights Inheritance in Stage 32 Lexicon (WP7).
"""

import pytest
from app.datasets.sinhala_lexicon.rights_resolver import LexiconRightsResolver
from app.datasets.sinhala_lexicon.schemas import RightsProfileReference
from app.datasets.sinhala_lexicon.enums import FieldExportPolicy

def test_version_pinned_rights_resolution():
    """Verify rights resolver resolves field policies and applies most restrictive rules."""
    resolver = LexiconRightsResolver()
    refs = [
        RightsProfileReference(source_id="SRC-1", rights_profile_id="RP-SRC-1", rights_profile_version=1),
        RightsProfileReference(source_id="SRC-2", rights_profile_id="RP-RESTRICTED-2", rights_profile_version=2)
    ]
    policies = resolver.resolve_entry_export_policies(refs)
    assert policies["canonical_form"] == FieldExportPolicy.METADATA_ONLY
    assert policies["concordance_contexts"] == FieldExportPolicy.RESTRICTED_PROTECTED_INTERNAL

def test_exact_equality_with_stage31_v8_source_registry():
    """
    Asserts exact equality between every Stage 32 inherited profile and Stage 31 v8 source registry.
    Ensures licence labels in Stage 32 are descriptive only and the authoritative rights decision is
    the exact rights_profile_id and rights_profile_version inherited from stage-31-complete-v8.
    """
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    approved_sources_path = repo_root / "data" / "sinhala_external" / "registry" / "approved_sources.json"
    draft_lexicon_path = repo_root / "data" / "sinhala_lexicon" / "lexicon" / "draft_lexicon.jsonl"

    assert approved_sources_path.exists(), "Approved sources registry must exist"
    with open(approved_sources_path, "r", encoding="utf-8") as f:
        src_data = json.load(f)

    # Authoritative Stage 31 v8 registry mapping
    authoritative_registry = {
        s["source_id"]: {
            "rights_profile_id": s["rights_profile_id"],
            "rights_profile_version": s["rights_profile_version"],
            "primary_decision": s["primary_decision"]
        }
        for s in src_data.get("sources", [])
    }

    # Pinned requirements check:
    assert authoritative_registry["SRC-SI-001"]["rights_profile_id"] == "RP-SRC-SI-001"
    assert authoritative_registry["SRC-SI-001"]["rights_profile_version"] == 1
    assert authoritative_registry["SRC-SI-002"]["rights_profile_id"] == "RP-SRC-SI-002"
    assert authoritative_registry["SRC-SI-002"]["rights_profile_version"] == 2  # Stage 31 v8 supersedes v1
    assert authoritative_registry["SRC-SI-003"]["rights_profile_id"] == "RP-SRC-SI-003"
    assert authoritative_registry["SRC-SI-003"]["rights_profile_version"] == 1
    assert authoritative_registry["SRC-SI-004"]["rights_profile_id"] == "RP-SRC-SI-004"
    assert authoritative_registry["SRC-SI-004"]["rights_profile_version"] == 1
    assert authoritative_registry["SRC-SI-008"]["rights_profile_id"] == "RP-SRC-SI-008"
    assert authoritative_registry["SRC-SI-008"]["rights_profile_version"] == 1

    if not draft_lexicon_path.exists():
        pytest.skip("draft_lexicon.jsonl not yet built")

    entries = []
    with open(draft_lexicon_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    assert len(entries) == 1010

    missing_rights_refs = 0
    unregistered_sources = 0
    src_si_002_count = 0

    for entry in entries:
        refs = entry.get("rights_profile_refs", [])
        if not refs:
            missing_rights_refs += 1
        for ref in refs:
            s_id = ref["source_id"]
            rp_id = ref["rights_profile_id"]
            rp_ver = ref["rights_profile_version"]

            if s_id not in authoritative_registry:
                unregistered_sources += 1
                continue

            expected = authoritative_registry[s_id]
            assert rp_id == expected["rights_profile_id"], (
                f"Entry {entry['entry_id']} has rights_profile_id {rp_id}, expected {expected['rights_profile_id']}"
            )
            assert rp_ver == expected["rights_profile_version"], (
                f"Entry {entry['entry_id']} has rights_profile_version {rp_ver}, expected {expected['rights_profile_version']}"
            )

            if s_id == "SRC-SI-002":
                src_si_002_count += 1
                assert rp_ver == 2, f"SRC-SI-002 must inherit version 2, got {rp_ver}"

    assert missing_rights_refs == 0
    assert unregistered_sources == 0
    assert src_si_002_count == 207

def test_entry_source_memberships_and_invariants():
    """
    Asserts separate accounting units between 1,010 distinct entries and 1,194 entry-source memberships.
    Enforces invariant: sum_{e=1}^{1010} |contributing sources_e| == 1,194.
    """
    import collections
    import json
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    draft_lexicon_path = repo_root / "data" / "sinhala_lexicon" / "lexicon" / "draft_lexicon.jsonl"
    if not draft_lexicon_path.exists():
        pytest.skip("draft_lexicon.jsonl not yet built")

    entries = []
    with open(draft_lexicon_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    assert len(entries) == 1010, "Must contain exactly 1,010 distinct lexicon entries"

    source_entry_counts = collections.Counter()
    multi_source_entries = 0
    single_source_entries = 0
    total_memberships = 0

    for entry in entries:
        refs = entry.get("rights_profile_refs", [])
        n_sources = len(refs)
        total_memberships += n_sources
        if n_sources == 1:
            single_source_entries += 1
        elif n_sources > 1:
            multi_source_entries += 1

        for ref in refs:
            source_entry_counts[ref["source_id"]] += 1

    # Invariant: sum of contributing sources per entry == 1,194
    assert total_memberships == 1194, f"Expected 1,194 entry-source memberships, got {total_memberships}"
    assert single_source_entries == 872
    assert multi_source_entries == 138
    assert single_source_entries + multi_source_entries == 1010

    # Source-specific contributing entries:
    assert source_entry_counts["SRC-SI-001"] == 448
    assert source_entry_counts["SRC-SI-002"] == 207
    assert source_entry_counts["SRC-SI-003"] == 179
    assert source_entry_counts["SRC-SI-004"] == 215
    assert source_entry_counts["SRC-SI-008"] == 145
    assert sum(source_entry_counts.values()) == 1194

