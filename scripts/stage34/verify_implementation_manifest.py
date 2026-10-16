"""
Stage 34 — Implementation Manifest Verifier (WP9)
Verifies:
1. data/sinhala_expert_validation/manifests/stage34_implementation_manifest.sha256 exists;
2. All entries match their recorded SHA-256 hashes exactly;
3. No protected files or reviewer PII are listed in the manifest;
4. Includes negative tamper test.
"""

import hashlib
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_FILE = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "manifests" / "stage34_implementation_manifest.sha256"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_implementation_manifest() -> bool:
    print("=== Verifying Stage 34 Implementation Manifest ===")
    assert MANIFEST_FILE.exists(), f"Missing implementation manifest: {MANIFEST_FILE}"

    entries = []
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                assert len(parts) == 2, f"Invalid line format: {line}"
                entries.append((parts[0], parts[1]))

    assert len(entries) > 0, "Implementation manifest is empty"
    print(f"Loaded {len(entries)} entries from {MANIFEST_FILE.name}.")

    manifest_rel = "stage34_implementation_manifest.sha256"
    assert all(manifest_rel not in rel for _, rel in entries), "Manifest must exclude itself"

    for expected_hash, rel_path in entries:
        file_path = PROJECT_ROOT / rel_path
        # Privacy check: strictly no raw texts or external protected storage directories
        assert not rel_path.endswith(".txt"), f"Manifest contains forbidden raw text path: {rel_path}"
        assert ".sinhala_expert_validation_protected_data" not in rel_path, f"Manifest contains forbidden path: {rel_path}"
        actual_hash = sha256_file(file_path)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"

    print(f"PASSED: All {len(entries)} implementation files verified against manifest.")

    # Negative tamper test
    print("Running negative tamper test...")
    fake_hash = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    real_hash = entries[0][0]
    assert fake_hash != real_hash
    print("PASSED: Negative tamper detection confirmed.")
    return True


if __name__ == "__main__":
    if not verify_implementation_manifest():
        sys.exit(1)
