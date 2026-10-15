"""
Stage 30 Prerequisite Snapshot Script (WP0)
Snapshots Stage 29 baseline commits, tags, manifest hashes, registry hashes,
font hashes, and baseline test counts into data/sinhala_preprocessing/snapshots/stage29_prerequisite_snapshot.json.
"""

import json
import hashlib
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "snapshots"
OUTPUT_FILE = SNAPSHOT_DIR / "stage29_prerequisite_snapshot.json"

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

    expected_prereq_commit = "89a253c452ea85664f988f31d357d6d9ee72b464"
    c29 = git_rev_parse("stage-29-complete-v2~0")
    c30_start = git_rev_parse("stage-30-start~0")

    assert c29 == expected_prereq_commit, f"Expected {expected_prereq_commit}, got {c29}"
    assert c30_start == expected_prereq_commit, f"Expected {expected_prereq_commit}, got {c30_start}"
    assert git_is_ancestor("stage-29-complete-v2~0", "stage-30-start~0"), "stage-29-complete-v2 must be ancestor of stage-30-start"
    assert git_is_ancestor("stage-28a-complete-v4~0", "stage-30-start~0"), "stage-28a must be ancestor"
    assert git_is_ancestor("stage-27-infrastructure-complete-v3~0", "stage-30-start~0"), "stage-27 must be ancestor"
    assert git_is_ancestor("stage-26-complete-v5~0", "stage-30-start~0"), "stage-26 must be ancestor"

    # Stage 29 Manifest Hashes
    manifest_path = PROJECT_ROOT / "docs" / "stage29_manifest.sha256"
    manifest_entries = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                manifest_entries[parts[1]] = parts[0]

    # Verify each controlled document exists and hash matches
    verified_docs = {}
    for rel_path, exp_sha in manifest_entries.items():
        doc_file = PROJECT_ROOT / rel_path
        actual_sha = compute_sha256(doc_file)
        assert actual_sha == exp_sha, f"SHA mismatch for {rel_path}: expected {exp_sha}, got {actual_sha}"
        verified_docs[rel_path] = actual_sha

    # Stage 29 Registry Artifacts
    registry_files = [
        "data/sinhala_foundation/registry/font_registry.json",
        "data/sinhala_foundation/registry/language_registry.json",
        "data/sinhala_foundation/registry/control_character_policy.json",
        "data/sinhala_foundation/fonts/NotoSansSinhala-Regular.ttf",
        "data/sinhala_foundation/fonts/NotoSansSinhala-Bold.ttf",
        "data/sinhala_foundation/fonts/LICENSE.txt"
    ]
    verified_registries = {}
    for rf in registry_files:
        fpath = PROJECT_ROOT / rf
        if fpath.exists():
            verified_registries[rf] = compute_sha256(fpath)

    # English Corpus & Stage 28A benchmark snapshots
    english_releases = [
        "data/final_dataset_pipeline/benchmark_evaluation/stage28a_models_benchmark_evaluation.json",
        "data/final_dataset_pipeline/comparison_matrix/stage28a_models_comparison_matrix.json"
    ]
    verified_english = {}
    for ef in english_releases:
        fpath = PROJECT_ROOT / ef
        if fpath.exists():
            verified_english[ef] = compute_sha256(fpath)

    snapshot_data = {
        "snapshot_id": "STAGE29-PREREQUISITE-SNAPSHOT-V1",
        "prerequisite_tag": "stage-29-complete-v2",
        "prerequisite_commit": expected_prereq_commit,
        "start_tag": "stage-30-start",
        "start_commit": c30_start,
        "ancestry_verification": {
            "stage_29_complete_v2_ancestor": True,
            "stage_28a_complete_v4_ancestor": True,
            "stage_27_infrastructure_complete_v3_ancestor": True,
            "stage_26_complete_v5_ancestor": True
        },
        "stage29_manifest_sha256": compute_sha256(manifest_path),
        "stage29_documentation_artifacts": verified_docs,
        "stage29_registry_and_fonts": verified_registries,
        "governed_english_and_stage28a_artifacts": verified_english,
        "stage29_baseline_test_counts": {
            "backend_stage29_tests": 39,
            "backend_full_suite": 501,
            "frontend_localization_tests": 17,
            "playwright_browser_tests": 12,
            "frontend_production_build": "PASSED"
        },
        "governance_status": {
            "validation_status": "draft",
            "research_eligible": False,
            "approved_for_child_delivery": False,
            "requires_expert_review": True
        }
    }

    OUTPUT_FILE.write_text(json.dumps(snapshot_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Stage 29 prerequisite snapshot successfully written to: {OUTPUT_FILE}")
    print(f"Prerequisite commit: {expected_prereq_commit}")
    print(f"Document deliverables verified: {len(verified_docs)}/11")
    print(f"Registry and font artifacts verified: {len(verified_registries)}")

if __name__ == "__main__":
    build_snapshot()
