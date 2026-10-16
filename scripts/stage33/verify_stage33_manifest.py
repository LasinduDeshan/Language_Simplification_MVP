"""
Stage 33 — Read-Only Manifest Verification Suite.
Verifies cryptographic integrity of documentation and implementation manifests
and executes negative tamper tests on temporary copies.
"""

import hashlib
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_MANIFEST = PROJECT_ROOT / "docs" / "stage33_manifest.sha256"
IMPLEMENTATION_MANIFEST = PROJECT_ROOT / "data" / "sinhala_simplification" / "manifests" / "stage33_implementation_manifest.sha256"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest(manifest_path: Path, label: str, expected_count: int) -> bool:
    print(f"\n--- Verifying {label} ({manifest_path.name}) ---")
    if not manifest_path.exists():
        print(f"FAILED: Manifest not found: {manifest_path}")
        return False

    entries = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                entries[parts[1]] = parts[0]

    print(f"Loaded {len(entries)} entries (Expected: {expected_count}).")
    if len(entries) != expected_count:
        print(f"FAILED: Entry count mismatch: expected {expected_count}, got {len(entries)}")
        return False

    all_ok = True
    for rel_path, exp_sha in entries.items():
        fp = PROJECT_ROOT / rel_path
        if not fp.exists():
            print(f"  [MISSING]  {rel_path}")
            all_ok = False
            continue
        actual_sha = compute_sha256(fp)
        if actual_sha != exp_sha:
            print(f"  [MISMATCH] {rel_path} (Expected {exp_sha[:16]}..., Actual {actual_sha[:16]}...)")
            all_ok = False
        else:
            print(f"  [OK]       {rel_path}")

    # Negative tamper test on temporary copy
    print(f"--- Running Temporary Artifact Tamper Detection Test on {label} ---")
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp_name = tmp.name
        # Write tampered first line
        first = True
        for rel_path, exp_sha in entries.items():
            if first:
                tampered_sha = "0" * 64
                tmp.write(f"{tampered_sha}  {rel_path}\n")
                first = False
            else:
                tmp.write(f"{exp_sha}  {rel_path}\n")

    try:
        # Verify tampered copy fails
        tampered_failed = False
        with open(tmp_name, "r", encoding="utf-8") as tf:
            for line in tf:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    fp = PROJECT_ROOT / parts[1]
                    if fp.exists() and compute_sha256(fp) != parts[0]:
                        tampered_failed = True
                        break
        assert tampered_failed, "Tampered copy unexpectedly passed verification!"
        print("  Original manifest modified: false")
        print("  Temporary artifact copy modified: true")
        print("  Hash mismatch detected: true")
        print("  Verifier returned failure for tampered copy: true")
    finally:
        Path(tmp_name).unlink(missing_ok=True)

    return all_ok


def verify_all_manifests():
    print("=== Stage 33 Read-Only Manifest Verification Suite ===")

    docs_ok = verify_manifest(DOCS_MANIFEST, "Planned Documentation Manifest", 14)
    impl_ok = verify_manifest(IMPLEMENTATION_MANIFEST, "Governed Implementation Manifest", 29)

    if docs_ok and impl_ok:
        print("\n=== OVERALL RESULT: ALL STAGE 33 MANIFESTS VERIFIED OK ===")
        print("14/14 Docs + 29/29 Implementation Artifacts, 0 Mismatches, Tamper Tests Passed.")
        return True
    else:
        print("\n=== OVERALL RESULT: STAGE 33 MANIFEST VERIFICATION FAILED ===")
        sys.exit(1)


if __name__ == "__main__":
    verify_all_manifests()
