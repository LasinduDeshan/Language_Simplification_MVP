"""
Stage 24 WP0: Snapshot Stage 23 baseline state, environment, and dataset release manifests.
"""
import os
import sys
import json
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime

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

def get_easse_info():
    try:
        import easse
        version = getattr(easse, "__version__", "installed")
        easse_path = getattr(easse, "__file__", "unknown")
        return {"installed": True, "version": str(version), "path": str(easse_path)}
    except ImportError:
        return {"installed": False, "version": None, "path": None}

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    snapshot_dir = repo_root / "data" / "baseline_simplification" / "registry"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    asset_rel_dir = repo_root / "data" / "external_english" / "releases" / "0.1.0"
    corpus_rel_dir = repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0"
    
    asset_manifest_sha = compute_sha256(asset_rel_dir / "release_manifest.sha256") if (asset_rel_dir / "release_manifest.sha256").exists() else None
    locked_test_manifest_sha = compute_sha256(corpus_rel_dir / "splits" / "locked_test_manifest.json") if (corpus_rel_dir / "splits" / "locked_test_manifest.json").exists() else None
    
    snapshot_data = {
        "stage": "Stage 24 WP0 Baseline Snapshot",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "git": {
            "head_commit": get_git_commit("HEAD"),
            "stage_23_complete_v2_commit": get_git_commit("stage-23-complete-v2^{commit}"),
            "stage_24_start_commit": get_git_commit("stage-24-start^{commit}"),
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "easse": get_easse_info()
        },
        "dataset_releases": {
            "external_english_asset_version": "0.1.0",
            "external_english_asset_manifest_sha256": asset_manifest_sha,
            "simplification_corpus_version": "0.2.0",
            "locked_test_manifest_sha256": locked_test_manifest_sha
        },
        "status": "frozen_baseline_ready"
    }
    
    out_file = snapshot_dir / "stage24_baseline_snapshot.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2)
        
    print(f"Snapshot successfully written to: {out_file}")
    print(json.dumps(snapshot_data, indent=2))

if __name__ == "__main__":
    main()
