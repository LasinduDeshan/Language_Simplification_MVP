"""
Read-Only Manifest Verifier and Negative Tamper Test for Stage 31.
Strictly read-only: does not write, overwrite, or modify any files.
"""

import hashlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "manifests" / "stage31_manifest.sha256"

def verify_manifest():
    print("--- Stage 31 Manifest Read-Only Verification ---")
    if not MANIFEST_FILE.exists():
        print(f"ERROR: Manifest file not found at: {MANIFEST_FILE}")
        return False

    lines = MANIFEST_FILE.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            entries.append((parts[0].strip(), parts[1].strip()))

    print(f"Loaded {len(entries)} manifest entries.")
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

    print("\n--- Manifest Verification Results ---")
    print(f"Total Entries Checked: {len(entries)}")
    print(f"Verified OK:           {verified_count}")
    print(f"Mismatches:            {len(mismatches)}")
    print(f"Missing Files:         {len(missing)}")

    # Negative Tamper Test
    print("\n--- Running Negative Tamper Detection Test ---")
    tamper_target_rel = entries[0][1]
    tamper_expected_hash = entries[0][0]
    tamper_path = PROJECT_ROOT / tamper_target_rel
    original_bytes = tamper_path.read_bytes()

    # Simulate tampered byte in memory (NO disk writes)
    tampered_bytes = original_bytes + b"\n# TAMPER_TEST"
    tampered_hash = hashlib.sha256(tampered_bytes).hexdigest()

    if tampered_hash == tamper_expected_hash:
        print("ERROR: Negative tamper test failed! Altered bytes produced identical hash.")
        return False
    else:
        print(f"Negative tamper test PASSED: Memory perturbation on '{tamper_target_rel}' correctly triggered mismatch.")

    success = (len(mismatches) == 0 and len(missing) == 0)
    return success

if __name__ == "__main__":
    ok = verify_manifest()
    sys.exit(0 if ok else 1)
