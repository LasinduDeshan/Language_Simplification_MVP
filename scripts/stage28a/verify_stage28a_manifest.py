"""
Stage 28A Comprehensive Deliverable Manifest Verifier.
Parses docs/stage28a_manifest.sha256, computes SHA-256 for every entry,
validates against required artifact list, checks for duplicates, and reports status.
"""
import sys
import hashlib
from pathlib import Path

REQUIRED_STAGE28A_ARTIFACTS = [
    "stage28a_implementation_plan.md",
    "stage28a_governance_and_scope.md",
    "stage28a_system_registry.csv",
    "stage28a_metric_protocol.md",
    "stage28a_internal_locked_comparison.csv",
    "stage28a_clean_subset_comparison.csv",
    "stage28a_asset_comparison.csv",
    "stage28a_safety_and_validation_report.md",
    "stage28a_latency_cost_report.csv",
    "stage28a_statistical_analysis.md",
    "stage28a_error_analysis.md",
    "stage28a_accounting_summary.md",
    "stage28a_reproducibility_record.json",
    "stage28a_completion_record.md",
]


def compute_file_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest().lower()


def verify_manifest(repo_root: Path) -> bool:
    docs_dir = repo_root / "docs"
    manifest_path = docs_dir / "stage28a_manifest.sha256"

    if not manifest_path.exists():
        print(f"[FAIL] Manifest file does not exist: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    parsed_entries = []
    seen_filenames = set()
    duplicate_count = 0

    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            print(f"[WARN] Malformed manifest line: {line}")
            continue
        expected_hash, fname = parts[0].strip().lower(), parts[1].strip()
        if fname in seen_filenames:
            duplicate_count += 1
            print(f"[ERROR] Duplicate entry in manifest: {fname}")
        seen_filenames.add(fname)
        parsed_entries.append((expected_hash, fname))

    total_expected = len(parsed_entries)
    verified_count = 0
    missing_count = 0
    mismatch_count = 0

    print(f"[*] Verifying Stage 28A Manifest: {manifest_path.name}")
    print(f"[*] Total entries in manifest: {total_expected}")

    for expected_hash, fname in parsed_entries:
        target_path = docs_dir / fname
        if not target_path.exists():
            print(f"  [-] MISSING: {fname}")
            missing_count += 1
            continue

        actual_hash = compute_file_sha256(target_path)
        if actual_hash != expected_hash:
            print(f"  [-] MISMATCH: {fname}")
            print(f"      Expected: {expected_hash}")
            print(f"      Actual:   {actual_hash}")
            mismatch_count += 1
        else:
            verified_count += 1

    # Check for unlisted required artifacts
    unlisted_required = []
    for req in REQUIRED_STAGE28A_ARTIFACTS:
        if req not in seen_filenames:
            unlisted_required.append(req)

    print("\n" + "=" * 50)
    print("STAGE 28A MANIFEST VERIFICATION REPORT")
    print("=" * 50)
    print(f"Expected artifacts:             {total_expected}")
    print(f"Verified artifacts:             {verified_count}")
    print(f"Missing:                        {missing_count}")
    print(f"Hash mismatches:                {mismatch_count}")
    print(f"Duplicate paths:                {duplicate_count}")
    print(f"Unlisted required artifacts:    {len(unlisted_required)}")
    print("=" * 50)

    if unlisted_required:
        print("[ERROR] Required artifacts missing from manifest:")
        for u in unlisted_required:
            print(f"  - {u}")

    passed = (
        verified_count == total_expected
        and missing_count == 0
        and mismatch_count == 0
        and duplicate_count == 0
        and len(unlisted_required) == 0
    )

    if passed:
        print("[PASSED] All artifacts are present, unique, and strictly verified.")
    else:
        print("[FAILED] Manifest verification failed.")

    return passed


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    success = verify_manifest(root)
    sys.exit(0 if success else 1)
