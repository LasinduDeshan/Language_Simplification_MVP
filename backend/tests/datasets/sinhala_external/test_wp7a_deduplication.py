"""
Unit tests for Stage 31 WP7A Deduplication Engine and Transitive Split Grouping.
"""

import pytest
from app.datasets.sinhala_external.deduplication import (
    DeduplicationEngine,
    resolve_most_restrictive_export_policy,
    get_token_shingles,
    compute_jaccard_similarity,
)

def test_resolve_most_restrictive_export_policy():
    """Validates that the most restrictive export policy is strictly selected."""
    # When combining public CC-BY and protected internal only, result must be PROTECTED_INTERNAL_ONLY
    assert resolve_most_restrictive_export_policy(
        ["PUBLIC_PERMITTED_CC_BY", "PROTECTED_INTERNAL_ONLY"]
    ) == "PROTECTED_INTERNAL_ONLY"

    # When combining CC-BY and CC-BY-SA, result must be CC-BY-SA
    assert resolve_most_restrictive_export_policy(
        ["PUBLIC_PERMITTED_CC_BY", "PUBLIC_PERMITTED_CC_BY_SA"]
    ) == "PUBLIC_PERMITTED_CC_BY_SA"

    # Blocked proprietary overrides all
    assert resolve_most_restrictive_export_policy(
        ["PUBLIC_PERMITTED_CC_BY", "BLOCKED_PROPRIETARY"]
    ) == "BLOCKED_PROPRIETARY"

def test_exact_duplicate_detection():
    """Tests grouping of exact duplicate text records."""
    engine = DeduplicationEngine()
    records = {
        "REC-1": "ශ්‍රී ලංකාවේ ඉතිහාසය අවුරුදු 2500කට වඩා ඈතට දිවයයි.",
        "REC-2": "සීගිරිය යනු ලෝක උරුම බලකොටුවකි.",
        "REC-3": "ශ්‍රී ලංකාවේ ඉතිහාසය අවුරුදු 2500කට වඩා ඈතට දිවයයි."  # Exact duplicate of REC-1
    }
    clusters = engine.find_exact_duplicates(records)
    # Must yield 2 clusters: one with [REC-1, REC-3], one with [REC-2]
    sizes = sorted(len(v) for v in clusters.values())
    assert sizes == [1, 2]

def test_near_duplicate_jaccard_similarity():
    """Tests near-duplicate detection with token shingles."""
    engine = DeduplicationEngine(candidate_similarity_threshold=0.80)
    # Two sentences differing by only one word
    text_a = "අධ්‍යාපන අමාත්‍යාංශය විසින් නව විෂය නිර්දේශ ලබන වාරයේ සිට ක්‍රියාත්මක කරනු ලැබේ."
    text_b = "අධ්‍යාපන අමාත්‍යාංශය විසින් නව විෂය නිර්දේශ ලබන වාරයේ සිට මෙරට ක්‍රියාත්මක කරනු ලැබේ."
    text_c = "සම්පූර්ණයෙන්ම වෙනස් මාතෘකාවක් පිළිබඳව ලියන ලද වෙනත් වාක්‍යයක් මෙන්න."

    records = {
        "REC-A": text_a,
        "REC-B": text_b,
        "REC-C": text_c
    }
    candidates = engine.find_near_duplicates(records)
    assert len(candidates) == 1
    cand = candidates[0]
    assert {cand.record_a, cand.record_b} == {"REC-A", "REC-B"}
    assert cand.similarity >= 0.80

def test_transitive_split_grouping_and_dev_component_isolation():
    """
    Tests that:
    1. Transitive links (doc group + near duplicate) merge records into a single split_group_id.
    2. Any component containing a dev record is marked TRAIN_ONLY_DEVELOPMENT_COMPONENT.
    3. Pure untouched components are marked UNTOUCHED_EVAL_ELIGIBLE_COMPONENT.
    """
    engine = DeduplicationEngine()
    all_records = ["REC-1", "REC-2", "REC-3", "REC-4", "REC-5"]
    
    # Doc group link: REC-1 and REC-2 share GRP-A
    doc_group_map = {
        "REC-1": "GRP-A",
        "REC-2": "GRP-A",
        "REC-3": "GRP-B",
        "REC-4": "GRP-C",
        "REC-5": "GRP-C"
    }
    # Near-duplicate link: REC-2 and REC-3
    confirmed_near = [("REC-2", "REC-3")]
    
    # Dev record: only REC-1 is in dev pool
    dev_records = {"REC-1"}

    rec_to_group, group_types = engine.build_transitive_split_groups(
        all_record_ids=all_records,
        doc_group_map=doc_group_map,
        exact_clusters={},
        confirmed_near_dups=confirmed_near,
        dev_records=dev_records
    )

    # REC-1, REC-2, REC-3 must share the SAME split_group_id transitively
    grp_1 = rec_to_group["REC-1"]
    grp_2 = rec_to_group["REC-2"]
    grp_3 = rec_to_group["REC-3"]
    assert grp_1 == grp_2 == grp_3

    # And because REC-1 is in dev_records, this group must be TRAIN_ONLY_DEVELOPMENT_COMPONENT
    assert group_types[grp_1] == "TRAIN_ONLY_DEVELOPMENT_COMPONENT"

    # REC-4 and REC-5 share GRP-C, and have no dev records
    grp_4 = rec_to_group["REC-4"]
    grp_5 = rec_to_group["REC-5"]
    assert grp_4 == grp_5
    assert grp_4 != grp_1
    assert group_types[grp_4] == "UNTOUCHED_EVAL_ELIGIBLE_COMPONENT"

def test_canonical_analytical_corpus_ledger():
    """
    Validates canonical analytical corpus properties:
    - Canonical analytical corpus present in manifest: true
    - Canonical records: 150
    - Noncanonical exact duplicates: 0
    - Canonical-to-provenance mapping failures: 0
    - Sum of provenance weights: 150.0
    """
    import json
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    canonical_file = project_root / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    provenance_file = project_root / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
    manifest_file = project_root / "data" / "sinhala_external" / "manifests" / "stage31_manifest.sha256"

    # 1. Canonical analytical corpus present in manifest
    manifest_text = manifest_file.read_text(encoding="utf-8")
    assert "data/sinhala_external/corpus/canonical_analytical_corpus.jsonl" in manifest_text

    # 2. Canonical records count: 150
    canonical_records = [json.loads(l) for l in canonical_file.read_text(encoding="utf-8").splitlines()]
    assert len(canonical_records) == 150

    # 3. Noncanonical exact duplicates: 0
    noncanonical_in_canonical_view = [r for r in canonical_records if not r.get("is_canonical_exact_record", False)]
    assert len(noncanonical_in_canonical_view) == 0

    # 4. Canonical-to-provenance mapping failures: 0
    provenance_records = [json.loads(l) for l in provenance_file.read_text(encoding="utf-8").splitlines()]
    provenance_ids = {r["record_id"] for r in provenance_records}
    canonical_mapping_failures = [
        r["record_id"] for r in provenance_records
        if r.get("canonical_record_id") not in provenance_ids
    ]
    assert len(canonical_mapping_failures) == 0

    # 5. Sum of provenance weights: 150.0
    total_weight = sum(r.get("exact_duplicate_weight", 0.0) for r in provenance_records)
    assert abs(total_weight - 150.0) < 1e-4
