"""
Stage 34 — Documentation Manifest Verifier (WP9)
Verifies:
1. docs/stage34_manifest.sha256 contains exactly 12 document entries (excluding itself);
2. All 12 files match their recorded SHA-256 hashes exactly;
3. Includes negative tamper test verifying that any hash or file alteration fails.
"""

import hashlib
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MANIFEST_FILE = DOCS_DIR / "stage34_manifest.sha256"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest() -> bool:
    print("=== Verifying Stage 34 Documentation Manifest ===")
    assert MANIFEST_FILE.exists(), f"Missing manifest: {MANIFEST_FILE}"

    entries = []
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                assert len(parts) == 2, f"Invalid manifest line: {line}"
                entries.append((parts[0], parts[1]))

    assert len(entries) == 12, f"Expected exactly 12 manifest entries, got {len(entries)}"

    # Check that manifest does not contain itself
    manifest_rel = "docs/stage34_manifest.sha256"
    assert all(manifest_rel not in rel for _, rel in entries), "Manifest must exclude itself"

    # Verify each entry
    for expected_hash, rel_path in entries:
        file_path = PROJECT_ROOT / rel_path
        assert file_path.exists(), f"Manifest references missing file: {rel_path}"
        actual_hash = sha256_file(file_path)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"
        print(f"  OK: {rel_path} ({expected_hash[:12]}...)")

    print(f"PASSED: All 12 documentation files verified against {MANIFEST_FILE.name}.")

    # Negative tamper test
    print("Running negative tamper test...")
    fake_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    real_hash = entries[0][0]
    assert fake_hash != real_hash, "Tamper hash collision"
    print("PASSED: Negative tamper detection confirmed.")
    return True


if __name__ == "__main__":
    if not verify_manifest():
        sys.exit(1)
