"""
Stage 30 Immutability Verifier.
Verifies that Stage 29 documentation, registry, and font artifacts,
as well as English corpus and Stage 28A artifacts, match the baseline snapshot.
"""

import sys
import json
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_PATH = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "snapshots" / "stage29_prerequisite_snapshot.json"

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_immutability():
    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(f"Snapshot missing: {SNAPSHOT_PATH}")

    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    docs = snapshot["stage29_documentation_artifacts"]
    registries = snapshot["stage29_registry_and_fonts"]
    english = snapshot["governed_english_and_stage28a_artifacts"]

    mismatches = 0
    checked = 0

    print("--- Verifying Stage 29 Documentation Artifacts ---")
    for rel_path, exp_sha in docs.items():
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            print(f"  MISSING: {rel_path}")
            mismatches += 1
            continue
        actual_sha = compute_sha256(p)
        if actual_sha == exp_sha:
            print(f"  OK: {rel_path}")
            checked += 1
        else:
            print(f"  MISMATCH: {rel_path}")
            mismatches += 1

    print("\n--- Verifying Stage 29 Registry and Font Artifacts ---")
    for rel_path, exp_sha in registries.items():
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            print(f"  MISSING: {rel_path}")
            mismatches += 1
            continue
        actual_sha = compute_sha256(p)
        if actual_sha == exp_sha:
            print(f"  OK: {rel_path}")
            checked += 1
        else:
            print(f"  MISMATCH: {rel_path}")
            mismatches += 1

    print("\n--- Verifying English and Stage 28A Artifacts ---")
    for rel_path, exp_sha in english.items():
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            print(f"  MISSING: {rel_path}")
            mismatches += 1
            continue
        actual_sha = compute_sha256(p)
        if actual_sha == exp_sha:
            print(f"  OK: {rel_path}")
            checked += 1
        else:
            print(f"  MISMATCH: {rel_path}")
            mismatches += 1

    print(f"\nImmutability verification: Checked={checked}, Mismatches={mismatches}")
    if mismatches == 0:
        print("Result: PASSED")
        return True
    else:
        print("Result: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    verify_immutability()
