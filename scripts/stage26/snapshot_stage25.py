"""
Stage 26 WP0: Snapshot Stage 25 baseline state, environment, and dataset release manifests.
"""
import os
import sys
import json
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def compute_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def get_git_commit(ref: str = "HEAD") -> str:
    try:
        res = subprocess.run(["git", "rev-parse", ref], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return f"unknown ({e})"

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    snapshot_dir = repo_root / "data" / "model_simplification" / "registry"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    corpus_rel_dir = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0"
    issue_register_path = corpus_rel_dir / "dataset_issue_register.json"
    pairs_path = corpus_rel_dir / "simplification_pairs.json"
    locked_test_path = corpus_rel_dir / "splits" / "locked_test_manifest.json"
    
    snapshot_data = {
        "stage": "Stage 26 WP0 Stage 25 Snapshot (Restart Plan v2.1.0)",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git": {
            "head_commit": get_git_commit("HEAD"),
            "stage_25_complete_v2_commit": get_git_commit("stage-25-complete-v2^{commit}"),
            "stage_26_v2_start_commit": get_git_commit("stage-26-v2-start^{commit}"),
            "branch": "feature/stage26-v2"
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform()
        },
        "dataset_releases": {
            "simplification_corpus_version": "0.2.0",
            "simplification_pairs_sha256": compute_sha256(pairs_path) if pairs_path.exists() else None,
            "locked_test_manifest_sha256": compute_sha256(locked_test_path) if locked_test_path.exists() else None,
            "dataset_issue_register_sha256": compute_sha256(issue_register_path) if issue_register_path.exists() else None
        }
    }
    
    out_file = snapshot_dir / "stage25_baseline_snapshot.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2)
        
    print(f"[+] Stage 25 snapshot written to: {out_file}")
    print(f"    HEAD Commit: {snapshot_data['git']['head_commit']}")
    print(f"    Stage 25 Prerequisite: {snapshot_data['git']['stage_25_complete_v2_commit']}")
    print(f"    Issue Register SHA-256: {snapshot_data['dataset_releases']['dataset_issue_register_sha256']}")

if __name__ == "__main__":
    main()
