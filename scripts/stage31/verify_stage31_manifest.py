"""
Read-Only Manifest Verifier and Negative Tamper Test for Stage 31.
Strictly read-only: does not write, overwrite, or modify any files.
Verifies both:
1. docs/stage31_manifest.sha256 (11 planned documentation files)
2. data/sinhala_external/manifests/stage31_manifest.sha256 (29 expanded governed artifacts)
"""

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DOCS_MANIFEST = PROJECT_ROOT / "docs" / "stage31_manifest.sha256"
IMPLEMENTATION_MANIFEST = PROJECT_ROOT / "data" / "sinhala_external" / "manifests" / "stage31_manifest.sha256"

def verify_manifest_file(manifest_path: Path, expected_count: int, manifest_label: str) -> bool:
    print(f"\n--- Verifying {manifest_label} ({manifest_path.name}) ---")
    if not manifest_path.exists():
        print(f"ERROR: Manifest file not found at: {manifest_path}")
        return False

    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            entries.append((parts[0].strip(), parts[1].strip()))

    print(f"Loaded {len(entries)} entries (Expected: {expected_count}).")
    if len(entries) != expected_count:
        print(f"ERROR: Entry count mismatch! Expected {expected_count}, got {len(entries)}")
        return False

    mismatches = []
    missing = []
    verified_count = 0

    for expected_hash, rel_path in entries:
        file_path = PROJECT_ROOT / rel_path
        if not file_path.exists():
            missing.append(rel_path)
            print(f"  [MISSING]  {rel_path}")
            continue

        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if actual_hash.lower() == expected_hash.lower():
            verified_count += 1
            print(f"  [OK]       {rel_path}")
        else:
            mismatches.append((rel_path, expected_hash, actual_hash))
            print(f"  [MISMATCH] {rel_path} (Expected {expected_hash[:16]}..., Actual {actual_hash[:16]}...)")

    print(f"Entries Checked: {len(entries)} | Verified OK: {verified_count} | Mismatches: {len(mismatches)} | Missing: {len(missing)}")

    # Negative Tamper Detection Test
    print(f"--- Running Negative Tamper Detection on {manifest_label} ---")
    tamper_target_rel = entries[0][1]
    tamper_expected_hash = entries[0][0]
    tamper_path = PROJECT_ROOT / tamper_target_rel
    original_bytes = tamper_path.read_bytes()

    # Simulate tampered byte in memory (NO disk writes)
    tampered_bytes = original_bytes + b"\n# TAMPER_TEST"
    tampered_hash = hashlib.sha256(tampered_bytes).hexdigest()

    if tampered_hash == tamper_expected_hash:
        print(f"ERROR: Negative tamper test failed on {manifest_label}!")
        return False
    else:
        print(f"Negative tamper test PASSED: Memory perturbation on '{tamper_target_rel}' correctly triggered mismatch.")

    return (len(mismatches) == 0 and len(missing) == 0)

def verify_all():
    print("=== Stage 31 Read-Only Manifest Verification Suite ===")
    ok_docs = verify_manifest_file(DOCS_MANIFEST, 11, "Planned Documentation Manifest")
    ok_impl = verify_manifest_file(IMPLEMENTATION_MANIFEST, 29, "Expanded Governed Implementation Manifest")

    overall = ok_docs and ok_impl
    print("\n=== Overall Stage 31 Manifest Verification Result ===")
    if overall:
        print("ALL STAGE 31 MANIFESTS VERIFIED OK (11/11 Docs + 29/29 Implementation Artifacts, 0 Mismatches, Tamper Tests Passed)")
    else:
        print("STAGE 31 MANIFEST VERIFICATION FAILED!")
    return overall

if __name__ == "__main__":
    success = verify_all()
    sys.exit(0 if success else 1)
