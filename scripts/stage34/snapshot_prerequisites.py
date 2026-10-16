"""
Stage 34 Prerequisite Snapshot Script (WP0)
Snapshots Stage 33 baseline commit, start tag, ancestors, Stage 30-33 core artifact hashes,
record counts, and external protected storage boundaries into:
data/sinhala_expert_validation/snapshots/stage33_prerequisite_snapshot.json.
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "snapshots"
OUTPUT_FILE = SNAPSHOT_DIR / "stage33_prerequisite_snapshot.json"

EXPECTED_PREREQUISITE_COMMIT = "74481f4d09beeba42ccb9b9c32ff994e372af5bf"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def git_rev_parse(rev: str) -> str:
    cmd = ["git", "rev-parse", rev]
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    cmd = ["git", "merge-base", "--is-ancestor", ancestor, descendant]
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    return res.returncode == 0


def build_snapshot():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    c33_v2 = git_rev_parse("stage-33-complete-v2^{commit}")
    c34_start = git_rev_parse("stage-34-start^{commit}")

    if c33_v2 != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected prerequisite commit {EXPECTED_PREREQUISITE_COMMIT}, got {c33_v2}")
    if c34_start != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected stage-34-start commit {EXPECTED_PREREQUISITE_COMMIT}, got {c34_start}")

    # Verify ancestral line
    ancestors_to_check = [
        "stage-33-complete-v2^{commit}",
        "stage-32-complete-v5^{commit}",
        "stage-31-complete-v8^{commit}",
        "stage-30-complete-v3^{commit}",
        "stage-29-complete-v2^{commit}",
        "stage-28a-complete-v4^{commit}",
        "stage-27-infrastructure-complete-v3^{commit}",
        "stage-26-complete-v5^{commit}",
    ]
    verified_ancestry = {}
    for tag_ref in ancestors_to_check:
        is_anc = git_is_ancestor(tag_ref, "stage-34-start^{commit}")
        assert is_anc, f"Ancestor check failed for {tag_ref}"
        verified_ancestry[tag_ref] = git_rev_parse(tag_ref)

    # Validate external protected storage root
    env_root = os.environ.get("SINHALA_EXPERT_VALIDATION_PROTECTED_ROOT")
    if env_root:
        protected_root = Path(env_root).resolve()
    else:
        protected_root = (Path.home() / ".sinhala_expert_validation_protected_data").resolve()

    protected_root.mkdir(parents=True, exist_ok=True)
    if protected_root.is_relative_to(PROJECT_ROOT):
        raise AssertionError(
            f"Security violation: protected root {protected_root} must NOT resolve inside working tree {PROJECT_ROOT}"
        )

    # Stage 31 Core Corpus Artifacts
    corpus_artifacts = [
        "data/sinhala_external/corpus/canonical_analytical_corpus.jsonl",
        "data/sinhala_external/corpus/pilot_corpus.jsonl",
        "data/sinhala_external/corpus/corpus_metadata.json",
        "data/sinhala_external/registry/stage31_configuration.json",
        "data/sinhala_external/registry/approved_sources.json",
        "data/sinhala_external/registry/method_development_predeclaration.json",
    ]
    verified_corpus = {}
    for ca in corpus_artifacts:
        cap = PROJECT_ROOT / ca
        if not cap.exists():
            raise FileNotFoundError(f"Missing authoritative Stage 31 corpus artifact: {ca}")
        verified_corpus[ca] = compute_sha256(cap)

    # Stage 32 Lexicon Artifacts
    lexicon_artifacts = [
        "data/sinhala_lexicon/lexicon/draft_lexicon.jsonl",
        "data/sinhala_lexicon/lexicon/review_queue.jsonl",
        "data/sinhala_lexicon/lexicon/public_metadata_export.jsonl",
        "data/sinhala_lexicon/ledgers/token_occurrence_ledger.jsonl",
        "data/sinhala_lexicon/ledgers/candidate_entry_ledger.jsonl",
        "data/sinhala_lexicon/ledgers/surface_form_mapping.jsonl",
        "data/sinhala_lexicon/ledgers/provenance_weight_ledger.jsonl",
        "data/sinhala_lexicon/ledgers/corpus_identity_ledger.json",
        "data/sinhala_lexicon/ledgers/weighted_parity_diagnostic.json",
        "data/sinhala_lexicon/registry/stage32_configuration.json",
    ]
    verified_lexicon = {}
    for la in lexicon_artifacts:
        lap = PROJECT_ROOT / la
        if not lap.exists():
            raise FileNotFoundError(f"Missing authoritative Stage 32 lexicon artifact: {la}")
        verified_lexicon[la] = compute_sha256(lap)

    # Stage 33 Simplification Artifacts
    simplification_artifacts = [
        "data/sinhala_simplification/registry/stage33_configuration.json",
        "data/sinhala_simplification/registry/rule_registry_public.json",
        "data/sinhala_simplification/registry/ranking_precedence.json",
        "data/sinhala_simplification/registry/protected_span_policy.json",
        "data/sinhala_simplification/ledgers/candidate_ledger.jsonl",
        "data/sinhala_simplification/ledgers/final_disposition_ledger.jsonl",
        "data/sinhala_simplification/ledgers/rule_attempt_ledger.jsonl",
        "data/sinhala_simplification/ledgers/transformation_trace_ledger.jsonl",
        "data/sinhala_simplification/ledgers/train_candidate_ledger.jsonl",
        "data/sinhala_simplification/ledgers/train_final_disposition_ledger.jsonl",
        "data/sinhala_simplification/ledgers/validation_candidate_ledger.jsonl",
        "data/sinhala_simplification/ledgers/validation_final_disposition_ledger.jsonl",
        "data/sinhala_simplification/ledgers/locked_test_candidate_ledger.jsonl",
        "data/sinhala_simplification/ledgers/locked_test_final_disposition_ledger.jsonl",
        "data/sinhala_simplification/evaluation/public_summary.json",
        "data/sinhala_simplification/manifests/stage33_implementation_manifest.sha256",
    ]
    verified_simplification = {}
    for sa in simplification_artifacts:
        sap = PROJECT_ROOT / sa
        if not sap.exists():
            raise FileNotFoundError(f"Missing authoritative Stage 33 simplification artifact: {sa}")
        verified_simplification[sa] = compute_sha256(sap)

    # Manifests
    manifest_artifacts = [
        "docs/stage30_manifest.sha256",
        "docs/stage31_manifest.sha256",
        "docs/stage32_manifest.sha256",
        "docs/stage33_manifest.sha256",
    ]
    verified_manifests = {}
    for ma in manifest_artifacts:
        map_ = PROJECT_ROOT / ma
        if not map_.exists():
            raise FileNotFoundError(f"Missing manifest artifact: {ma}")
        verified_manifests[ma] = compute_sha256(map_)

    # Canonical analytical corpus counts & verification
    canonical_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    canonical_records = []
    with open(canonical_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                canonical_records.append(json.loads(line))
    canonical_count = len(canonical_records)

    split_counts = {}
    dev_split_counts = {}
    for r in canonical_records:
        s = r.get("split", "unknown")
        dev = r.get("is_method_development_record", False)
        split_counts[s] = split_counts.get(s, 0) + 1
        dev_split_counts[(s, dev)] = dev_split_counts.get((s, dev), 0) + 1

    assert canonical_count == 150, f"Expected 150 canonical records, got {canonical_count}"
    assert split_counts == {"train": 124, "validation": 13, "locked_test": 13}, f"Unexpected split counts: {split_counts}"

    # Stage 33 candidates count
    s33_cand_file = PROJECT_ROOT / "data" / "sinhala_simplification" / "ledgers" / "candidate_ledger.jsonl"
    with open(s33_cand_file, "r", encoding="utf-8") as f:
        s33_candidate_count = sum(1 for line in f if line.strip())

    s33_disp_file = PROJECT_ROOT / "data" / "sinhala_simplification" / "ledgers" / "final_disposition_ledger.jsonl"
    with open(s33_disp_file, "r", encoding="utf-8") as f:
        s33_disposition_count = sum(1 for line in f if line.strip())

    assert s33_disposition_count == 150, f"Expected 150 disposition records, got {s33_disposition_count}"

    snapshot_data = {
        "stage": "stage34",
        "workflow": "WP0_prerequisite_snapshot",
        "prerequisite_tag": "stage-33-complete-v2",
        "prerequisite_commit": EXPECTED_PREREQUISITE_COMMIT,
        "start_tag": "stage-34-start",
        "start_commit": c34_start,
        "verified_ancestors": verified_ancestry,
        "protected_storage_root": str(protected_root),
        "protected_storage_external_verified": True,
        "stage33_partition_finding": (
            "No partition leakage was detected under the frozen record, "
            "document-group, and method-development relations."
        ),
        "corpus_counts": {
            "canonical_total": canonical_count,
            "train": split_counts["train"],
            "validation": split_counts["validation"],
            "locked_test": split_counts["locked_test"],
        },
        "stage33_ledgers": {
            "candidate_count": s33_candidate_count,
            "disposition_count": s33_disposition_count,
        },
        "verified_hashes": {
            "corpus": verified_corpus,
            "lexicon": verified_lexicon,
            "simplification": verified_simplification,
            "manifests": verified_manifests,
        },
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

    print(f"Stage 34 prerequisite snapshot successfully generated at: {OUTPUT_FILE}")
    print(f"Ancestry verified: {len(verified_ancestry)} checkpoints")
    print(
        f"Stage 31 canonical: {canonical_count} (train: {split_counts['train']}, val: {split_counts['validation']}, test: {split_counts['locked_test']})"
    )
    print(f"Stage 33 candidates: {s33_candidate_count} | dispositions: {s33_disposition_count}")


if __name__ == "__main__":
    build_snapshot()
