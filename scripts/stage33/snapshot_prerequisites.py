"""
Stage 33 Prerequisite Snapshot Script (WP0)
Snapshots Stage 32 baseline commit, start tag, ancestors, Stage 31/32 core artifact hashes,
record counts, and protected storage boundaries into:
data/sinhala_simplification/snapshots/stage32_prerequisite_snapshot.json.
"""

import json
import hashlib
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "sinhala_simplification" / "snapshots"
OUTPUT_FILE = SNAPSHOT_DIR / "stage32_prerequisite_snapshot.json"

EXPECTED_PREREQUISITE_COMMIT = "7c6bb81a744305c3a59100a2c2af8fc06deb01c8"


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

    c32_v5 = git_rev_parse("stage-32-complete-v5^{commit}")
    c33_start = git_rev_parse("stage-33-start^{commit}")

    if c32_v5 != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected prerequisite commit {EXPECTED_PREREQUISITE_COMMIT}, got {c32_v5}")
    if c33_start != EXPECTED_PREREQUISITE_COMMIT:
        raise AssertionError(f"Expected stage-33-start commit {EXPECTED_PREREQUISITE_COMMIT}, got {c33_start}")

    # Verify ancestral line
    ancestors_to_check = [
        "stage-32-complete-v5^{commit}",
        "stage-31-complete-v8^{commit}",
        "stage-30-complete-v3^{commit}",
        "stage-29-complete-v2^{commit}",
        "stage-28a-complete-v4^{commit}",
        "stage-27-infrastructure-complete-v3^{commit}",
        "stage-26-complete-v5^{commit}"
    ]
    verified_ancestry = {}
    for tag_ref in ancestors_to_check:
        is_anc = git_is_ancestor(tag_ref, "stage-33-start^{commit}")
        assert is_anc, f"Ancestor check failed for {tag_ref}"
        verified_ancestry[tag_ref] = git_rev_parse(tag_ref)

    # Validate external protected storage root
    env_root = os.environ.get("SINHALA_SIMPLIFICATION_PROTECTED_ROOT")
    if env_root:
        protected_root = Path(env_root).resolve()
    else:
        protected_root = (Path.home() / ".sinhala_simplification_protected_data").resolve()
    
    protected_root.mkdir(parents=True, exist_ok=True)
    if protected_root.is_relative_to(PROJECT_ROOT):
        raise AssertionError(f"Security violation: protected root {protected_root} must NOT resolve inside working tree {PROJECT_ROOT}")

    # Stage 31 Core Corpus Artifacts
    corpus_artifacts = [
        "data/sinhala_external/corpus/canonical_analytical_corpus.jsonl",
        "data/sinhala_external/corpus/pilot_corpus.jsonl",
        "data/sinhala_external/corpus/corpus_metadata.json",
        "data/sinhala_external/registry/stage31_configuration.json",
        "data/sinhala_external/registry/approved_sources.json",
        "data/sinhala_external/registry/method_development_predeclaration.json"
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
        "data/sinhala_lexicon/registry/stage32_configuration.json"
    ]
    verified_lexicon = {}
    for la in lexicon_artifacts:
        lap = PROJECT_ROOT / la
        if not lap.exists():
            raise FileNotFoundError(f"Missing authoritative Stage 32 lexicon artifact: {la}")
        verified_lexicon[la] = compute_sha256(lap)

    # Counts & Splits in Canonical Corpus
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

    pilot_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
    with open(pilot_file, "r", encoding="utf-8") as f:
        pilot_count = sum(1 for line in f if line.strip())

    cand_file = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
    with open(cand_file, "r", encoding="utf-8") as f:
        cand_count = sum(1 for line in f if line.strip())

    occ_file = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "token_occurrence_ledger.jsonl"
    with open(occ_file, "r", encoding="utf-8") as f:
        occ_count = sum(1 for line in f if line.strip())

    weight_file = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "provenance_weight_ledger.jsonl"
    with open(weight_file, "r", encoding="utf-8") as f:
        weight_count = sum(1 for line in f if line.strip())

    assert canonical_count == 150, f"Expected 150 canonical records, got {canonical_count}"
    assert pilot_count == 180, f"Expected 180 pilot records, got {pilot_count}"
    assert cand_count == 1010, f"Expected 1010 candidate records, got {cand_count}"
    assert occ_count == 4072, f"Expected 4072 occurrence records, got {occ_count}"
    assert weight_count == 180, f"Expected 180 weight records, got {weight_count}"
    assert split_counts == {"train": 124, "validation": 13, "locked_test": 13}, f"Unexpected split counts: {split_counts}"

    snapshot_data = {
        "stage": "stage33",
        "workflow": "WP0_prerequisite_snapshot",
        "prerequisite_tag": "stage-32-complete-v5",
        "prerequisite_commit": EXPECTED_PREREQUISITE_COMMIT,
        "start_tag": "stage-33-start",
        "start_commit": c33_start,
        "verified_ancestors": verified_ancestry,
        "protected_storage_root": str(protected_root),
        "primary_evaluation_corpus_view": "canonical_analytical_150",
        "stage31_counts": {
            "canonical_analytical_records": canonical_count,
            "pilot_provenance_records": pilot_count,
            "surplus_duplicate_records": pilot_count - canonical_count,
            "splits": split_counts,
            "method_development_split_distribution": {f"{k[0]}_dev_{k[1]}": v for k, v in dev_split_counts.items()}
        },
        "stage32_counts": {
            "distinct_candidate_entries": cand_count,
            "total_token_occurrences": occ_count,
            "provenance_weight_records": weight_count
        },
        "verified_stage31_corpus_artifacts": verified_corpus,
        "verified_stage32_lexicon_artifacts": verified_lexicon
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)

    print(f"Stage 33 prerequisite snapshot successfully generated at: {OUTPUT_FILE}")
    print(f"Ancestry verified: {len(verified_ancestry)} checkpoints")
    print(f"Stage 31 canonical: {canonical_count} (train: {split_counts['train']}, val: {split_counts['validation']}, test: {split_counts['locked_test']})")
    print(f"Stage 32 candidates: {cand_count} | Occurrences: {occ_count} | Weights: {weight_count}")


if __name__ == "__main__":
    build_snapshot()
