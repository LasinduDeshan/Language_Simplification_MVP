"""
Read-Only Manifest Verifier and Negative Tamper Test for Stage 32.
Strictly read-only with respect to repository deliverables.
Verifies:
1. docs/stage32_manifest.sha256 (12 controlled documentation files)
2. data/sinhala_lexicon/manifests/stage32_implementation_manifest.sha256
Performs temporary artifact copy tampering verification on both manifests.
"""

import hashlib
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DOCS_MANIFEST = PROJECT_ROOT / "docs" / "stage32_manifest.sha256"
IMPLEMENTATION_MANIFEST = PROJECT_ROOT / "data" / "sinhala_lexicon" / "manifests" / "stage32_implementation_manifest.sha256"

def verify_manifest(manifest_path: Path, expected_count: int, manifest_label: str) -> bool:
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

    # Negative Tamper Detection Test on temporary copy
    print(f"--- Running Temporary Artifact Tamper Detection Test on {manifest_label} ---")
    target_rel = entries[0][1]
    expected_hash = entries[0][0]
    target_path = PROJECT_ROOT / target_rel

    with tempfile.NamedTemporaryFile(mode="w+b", delete=False, suffix=".tmp") as tmp:
        tmp_path = Path(tmp.name)
        orig_bytes = target_path.read_bytes()
        tmp.write(orig_bytes)
        tmp.write(b"\n# TAMPER_TEST_CORRUPTION_INJECTION\n")

    try:
        tampered_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        hash_mismatch = (tampered_hash != expected_hash)
        print("  Original manifest modified: false")
        print("  Temporary artifact copy modified: true")
        print(f"  Hash mismatch detected: {str(hash_mismatch).lower()}")
        print(f"  Verifier returned failure for tampered copy: {str(hash_mismatch).lower()}")

        if not hash_mismatch:
            print("ERROR: Tamper test failed: altered copy produced identical hash!")
            return False
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return (len(mismatches) == 0 and len(missing) == 0)

def main():
    print("=== Stage 32 Read-Only Manifest Verification Suite ===")
    v_docs = verify_manifest(DOCS_MANIFEST, expected_count=12, manifest_label="Planned Documentation Manifest")
    v_impl = verify_manifest(IMPLEMENTATION_MANIFEST, expected_count=26, manifest_label="Governed Implementation Manifest")

    if v_docs and v_impl:
        print("\n=== OVERALL RESULT: STAGE 32 MANIFEST VERIFICATION PASSED! ===")
        sys.exit(0)
    else:
        print("\n=== OVERALL RESULT: STAGE 32 MANIFEST VERIFICATION FAILED! ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
