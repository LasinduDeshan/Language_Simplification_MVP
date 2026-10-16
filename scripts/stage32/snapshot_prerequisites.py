"""
Stage 32 Prerequisite Snapshot Script (WP0)
Snapshots Stage 31 baseline commits, tags, ancestry, documentation manifest hashes,
corpus artifact hashes, and environment boundaries into:
data/sinhala_lexicon/snapshots/stage31_prerequisite_snapshot.json.
"""

import json
import hashlib
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "sinhala_lexicon" / "snapshots"
OUTPUT_FILE = SNAPSHOT_DIR / "stage31_prerequisite_snapshot.json"

EXPECTED_PREREQUISITE_COMMIT = "9096cfbf5d6e237c388e6c306dc12f13023875ba"

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

    c31_v8 = git_rev_parse("stage-31-complete-v8^{commit}")
    c32_start = git_rev_parse("stage-32-start^{commit}")

    if c31_v8 != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected prerequisite commit {EXPECTED_PREREQUISITE_COMMIT}, got {c31_v8}")
    if c32_start != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected stage-32-start commit {EXPECTED_PREREQUISITE_COMMIT}, got {c32_start}")

    # Verify ancestral line
    ancestors_to_check = [
        "stage-31-complete-v8^{commit}",
        "stage-30-complete-v3^{commit}",
        "stage-29-complete-v2^{commit}",
        "stage-28a-complete-v4^{commit}",
        "stage-27-infrastructure-complete-v3^{commit}",
        "stage-26-complete-v5^{commit}"
    ]
    verified_ancestry = {}
    for tag_ref in ancestors_to_check:
        is_anc = git_is_ancestor(tag_ref, "stage-32-start^{commit}")
        assert is_anc, f"Ancestor check failed for {tag_ref}"
        verified_ancestry[tag_ref] = git_rev_parse(tag_ref)

    # Validate external protected storage root
    env_root = os.environ.get("SINHALA_LEXICON_PROTECTED_ROOT")
    if env_root:
        protected_root = Path(env_root).resolve()
    else:
        protected_root = (Path.home() / ".sinhala_lexicon_protected_data").resolve()
    
    protected_root.mkdir(parents=True, exist_ok=True)
    if protected_root.is_relative_to(PROJECT_ROOT):
        raise AssertionError(f"Security violation: protected root {protected_root} must NOT resolve inside working tree {PROJECT_ROOT}")

    # Stage 31 Documentation Manifest
    manifest_path = PROJECT_ROOT / "docs" / "stage31_manifest.sha256"
    manifest_entries = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                manifest_entries[parts[1]] = parts[0]

    verified_docs = {}
    for rel_path, exp_sha in manifest_entries.items():
        doc_file = PROJECT_ROOT / rel_path
        actual_sha = compute_sha256(doc_file)
        if actual_sha != exp_sha:
            raise AssertionError(f"SHA mismatch for {rel_path}: expected {exp_sha}, got {actual_sha}")
        verified_docs[rel_path] = actual_sha

    # Stage 31 Core Corpus Artifacts
    corpus_artifacts = [
        "data/sinhala_external/corpus/canonical_analytical_corpus.jsonl",
        "data/sinhala_external/corpus/pilot_corpus.jsonl",
        "data/sinhala_external/corpus/corpus_metadata.json",
        "data/sinhala_external/registry/stage31_configuration.json",
        "data/sinhala_external/registry/approved_sources.json",
        "data/sinhala_external/registry/candidate_sources.json",
        "data/sinhala_external/registry/method_development_predeclaration.json"
    ]
    verified_corpus = {}
    for ca in corpus_artifacts:
        cap = PROJECT_ROOT / ca
        if not cap.exists():
            raise FileNotFoundError(f"Missing authoritative Stage 31 corpus artifact: {ca}")
        verified_corpus[ca] = compute_sha256(cap)

    # Count canonical and provenance records
    canonical_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    with open(canonical_file, "r", encoding="utf-8") as f:
        canonical_count = sum(1 for line in f if line.strip())

    provenance_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
    with open(provenance_file, "r", encoding="utf-8") as f:
        provenance_count = sum(1 for line in f if line.strip())

    assert canonical_count == 150, f"Expected 150 canonical records, got {canonical_count}"
    assert provenance_count == 180, f"Expected 180 provenance records, got {provenance_count}"

    snapshot_data = {
        "stage": "stage32",
        "workflow": "WP0_prerequisite_snapshot",
        "prerequisite_tag": "stage-31-complete-v8",
        "prerequisite_commit": EXPECTED_PREREQUISITE_COMMIT,
        "start_tag": "stage-32-start",
        "start_commit": c32_start,
        "verified_ancestors": verified_ancestry,
        "protected_storage_root": str(protected_root),
        "canonical_analytical_records": canonical_count,
        "provenance_records": provenance_count,
        "surplus_duplicate_records": provenance_count - canonical_count,
        "verified_stage31_documentation": verified_docs,
        "verified_stage31_corpus_artifacts": verified_corpus
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

    print(f"Prerequisite snapshot successfully generated at: {OUTPUT_FILE}")
    print(f"Canonical records: {canonical_count} | Provenance records: {provenance_count}")

if __name__ == "__main__":
    build_snapshot()
