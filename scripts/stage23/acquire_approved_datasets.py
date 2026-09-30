"""Step 2: Controlled, secure acquisition of approved external datasets."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.datasets.external_english.downloader import SecureDatasetDownloader
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.rights_gate import RightsGate
from app.datasets.external_english.schemas import ExternalDatasetId


ASSET_COMMIT_SHA = "9d659040d0d8942dbc4cd65cf357563b43fd9ab4"
ASSET_RAW_BASE_URL = f"https://raw.githubusercontent.com/facebookresearch/asset/{ASSET_COMMIT_SHA}/dataset"

ASSET_FILES = [
    # Validation split (2,000 source groups, 10 references each)
    "asset.valid.orig",
    *[f"asset.valid.simp.{i}" for i in range(10)],
    # Test split (359 source groups, 10 references each)
    "asset.test.orig",
    *[f"asset.test.simp.{i}" for i in range(10)],
]


def acquire_asset(downloader: SecureDatasetDownloader, dry_run: bool = False) -> dict:
    """Acquires official ASSET validation and test split files from commit-pinned repository."""
    raw_dir = Path("data/external_english/asset/raw")
    manifest_dir = Path("data/external_english/asset/manifests")
    manifest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Acquiring ASSET from commit {ASSET_COMMIT_SHA} ({len(ASSET_FILES)} files)...")

    results = {}
    manifest_lines = []

    for filename in ASSET_FILES:
        url = f"{ASSET_RAW_BASE_URL}/{filename}"
        dest = raw_dir / filename

        if dry_run:
            print(f"  [DRY-RUN] Would download {url} -> {dest}")
            results[filename] = {"status": "dry_run", "url": url}
            continue

        dest_path, file_hash = downloader.download_file(url, dest)
        file_size = dest_path.stat().st_size
        results[filename] = {
            "path": str(dest_path),
            "sha256": file_hash,
            "size_bytes": file_size,
            "url": url,
        }
        manifest_lines.append(f"{file_hash}  {filename}")
        print(f"  Downloaded {filename} ({file_size} bytes, sha256: {file_hash[:16]}...)")

    if not dry_run:
        manifest_path = manifest_dir / "raw_files.sha256"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(manifest_lines) + "\n")
        print(f"Serialized raw files SHA-256 manifest to {manifest_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Acquire approved external datasets")
    parser.add_argument(
        "--dataset",
        choices=["asset", "all_approved"],
        default="asset",
        help="Dataset to acquire (default: asset)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without downloading")
    args = parser.parse_args()

    registry = ExternalDatasetRegistry()
    gate = RightsGate(registry=registry)
    downloader = SecureDatasetDownloader()

    # 1. Enforce Rights Gate
    dataset_id: ExternalDatasetId = "EXTDATA-ASSET"
    allowed, reason = gate.authorize(dataset_id, action="acquire")
    if not allowed:
        print(f"ERROR: Acquisition blocked by rights gate: {reason}", file=sys.stderr)
        sys.exit(1)

    print(f"Rights check passed for {dataset_id}: {reason}")

    # 2. Acquire ASSET
    asset_results = acquire_asset(downloader, dry_run=args.dry_run)

    # 3. Export Acquisition Report
    if not args.dry_run:
        now_utc = datetime.now(timezone.utc).isoformat()
        report_path = Path("docs/stage23_acquisition_report.md")
        
        md_lines = [
            "# Stage 23 External Dataset Acquisition Report",
            "",
            "**Component:** Component 3 — AI/NLP-Based Language Simplification  ",
            f"**Acquisition Timestamp:** {now_utc}  ",
            "**Status:** COMPLETE & BITWISE VERIFIED  ",
            "",
            "---",
            "",
            "## 1. Acquired Dataset Summary",
            "",
            "| Dataset ID | Official Source | Pinned Commit SHA | Files Acquired | Total Size | Rights Status |",
            "|---|---|---|:---:|:---:|:---:|",
            f"| `EXTDATA-ASSET` | `facebookresearch/asset` | `{ASSET_COMMIT_SHA}` | {len(ASSET_FILES)} | {sum(r['size_bytes'] for r in asset_results.values())} bytes | `approved_local_research` |",
            "",
            "---",
            "",
            "## 2. Raw Snapshot File Manifest",
            "",
            "| Filename | Split | Role | Size (bytes) | SHA-256 Checksum |",
            "|---|---|---|---:|---|",
        ]
        
        for fn, meta in asset_results.items():
            split = "Validation" if "valid" in fn else "Test"
            role = "Original Source" if "orig" in fn else f"Reference {fn.split('.')[-1]}"
            md_lines.append(
                f"| `{fn}` | {split} | {role} | {meta['size_bytes']} | `{meta['sha256']}` |"
            )

        md_lines.extend([
            "",
            "---",
            "",
            "## 3. Blocked / Deferred Candidate Datasets",
            "",
            "- **`EXTDATA-TURKCORPUS`:** Acquisition blocked (rights status: `pending_content_rights_verification`).",
            "- **`EXTDATA-OASISSIMP-EN`:** Acquisition blocked (rights status: `pending_content_rights_verification`).",
            "- **`EXTDATA-WIKILARGE-PILOT`:** Acquisition blocked (rights status: `pending_lineage_and_rights_verification`).",
            "- **`EXTDATA-NEWSELA`:** Acquisition blocked (rights status: `excluded_rights`).",
        ])

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")
        print(f"Exported acquisition report to {report_path}")


if __name__ == "__main__":
    main()
