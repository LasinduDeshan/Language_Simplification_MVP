"""Snapshot and verify baseline before Stage 23 external dataset integration."""

import hashlib
import json
from pathlib import Path
import sys

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("Executing Stage 23 Baseline Checkpoint & Snapshot...")
    
    # 1. Verify Stage 22 Release Artifacts exist
    stage22_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0")
    if not stage22_dir.exists():
        print(f"ERROR: Stage 22 release directory not found at {stage22_dir}", file=sys.stderr)
        sys.exit(1)
        
    manifest_file = stage22_dir / "manifests" / "stage22_manifest.sha256"
    if not manifest_file.exists():
        print(f"ERROR: Stage 22 manifest not found at {manifest_file}", file=sys.stderr)
        sys.exit(1)
        
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_lines = [line.strip() for line in f if line.strip()]
        
    verified_files = 0
    for line in manifest_lines:
        expected_hash, rel_path = line.split("  ", 1)
        target_path = stage22_dir / rel_path
        if not target_path.exists():
            print(f"ERROR: Missing Stage 22 file {target_path}", file=sys.stderr)
            sys.exit(1)
        actual_hash = compute_sha256(target_path)
        if actual_hash != expected_hash:
            print(f"ERROR: Hash mismatch for {rel_path}: expected {expected_hash}, got {actual_hash}", file=sys.stderr)
            sys.exit(1)
        verified_files += 1
        
    print(f"Verified {verified_files} Stage 22 files against SHA-256 manifest.")
    
    # 2. Record Baseline State Evidence
    baseline_evidence = {
        "stage": "stage_23_start_checkpoint",
        "timestamp": "2026-09-29T16:25:00Z",
        "internal_release_version": "0.2.0",
        "preprocessing_pipeline_version": "1.0.0",
        "complexity_classifier_version": "1.0.0",
        "stage22_verified_files": verified_files,
        "stage22_manifest_sha256": compute_sha256(manifest_file),
    }
    
    snapshot_meta_path = Path("data/external_english/registry/stage23_baseline_snapshot.json")
    snapshot_meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(snapshot_meta_path, "w", encoding="utf-8") as f:
        json.dump(baseline_evidence, f, indent=2)
        
    print(f"Stage 23 Baseline snapshot metadata saved to {snapshot_meta_path}")
    print("WP0 Baseline Checkpoint COMPLETE.")

if __name__ == "__main__":
    main()
