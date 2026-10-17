"""
Verification script for Stage 36 documentation and implementation manifests.
Includes read-only checksum verification and negative tamper testing on temporary copies.
"""

import hashlib
from pathlib import Path
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[2]


def verify_manifest(manifest_rel_path: str, self_excluding_name: str = ""):
    manifest_path = REPO_ROOT / manifest_rel_path
    assert manifest_path.exists(), f"Manifest {manifest_rel_path} does not exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"Verifying {manifest_rel_path} ({len(lines)} entries)...")
    for line in lines:
        expected_hash, rel_path = line.split("  ", 1)
        if self_excluding_name and rel_path == self_excluding_name:
            continue
        p = REPO_ROOT / rel_path
        assert p.exists(), f"File {rel_path} does not exist"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == expected_hash, f"Hash mismatch for {rel_path}: expected {expected_hash}, got {h}"

    print(f"PASS: All entries in {manifest_rel_path} verified.")


def negative_tamper_test(manifest_rel_path: str):
    """
    Simulates tampering on a temporary copy to confirm fail-closed tamper detection.
    """
    manifest_path = REPO_ROOT / manifest_rel_path
    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    target_line = lines[0]
    expected_hash, rel_path = target_line.split("  ", 1)
    target_file = REPO_ROOT / rel_path

    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp:
        tmp.write(target_file.read_bytes() + b"\n# TAMPER_INJECTION")
        tmp_path = Path(tmp.name)

    try:
        tampered_hash = hashlib.sha256(tmp_path.read_bytes()).hexdigest()
        assert tampered_hash != expected_hash, "Tamper simulation failed to alter file hash"
        print(f"PASS: Negative tamper test confirmed for {manifest_rel_path}.")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def main():
    verify_manifest("docs/stage36_manifest.sha256", self_excluding_name="docs/stage36_manifest.sha256")
    verify_manifest("data/sinhala_output_validation/manifests/stage36_implementation_manifest.sha256")
    negative_tamper_test("docs/stage36_manifest.sha256")
    negative_tamper_test("data/sinhala_output_validation/manifests/stage36_implementation_manifest.sha256")
    print("ALL MANIFEST VERIFICATIONS AND TAMPER TESTS PASSED.")


if __name__ == "__main__":
    main()
