"""
Stage 29 WP0: Snapshot prerequisites, git ancestry, database record counts, and dataset releases.
"""
import os
import sys
import json
import hashlib
import platform
import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

def compute_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

def run_cmd(cmd: list) -> tuple:
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    snapshot_dir = repo_root / "data" / "sinhala_foundation" / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    print("[*] Verifying Git ancestry and prerequisites...")
    rc_28a, _, _ = run_cmd(["git", "merge-base", "--is-ancestor", "stage-28a-complete-v4^{commit}", "HEAD"])
    rc_26, _, _ = run_cmd(["git", "merge-base", "--is-ancestor", "stage-26-complete-v5^{commit}", "HEAD"])
    rc_27, _, _ = run_cmd(["git", "merge-base", "--is-ancestor", "stage-27-infrastructure-complete-v3^{commit}", "HEAD"])

    _, head_commit, _ = run_cmd(["git", "rev-parse", "HEAD"])
    _, start_commit, _ = run_cmd(["git", "rev-parse", "stage-29-start^{commit}"])
    _, v4_commit, _ = run_cmd(["git", "rev-parse", "stage-28a-complete-v4^{commit}"])
    _, branch, _ = run_cmd(["git", "branch", "--show-current"])

    ancestry_ok = (rc_28a == 0 and rc_26 == 0 and rc_27 == 0)
    commits_match = (start_commit == v4_commit == "0e83898a1272ecd8af2fc93f607e694ca07954cf")

    print(f"    Ancestry 28A: {'PASSED' if rc_28a == 0 else 'FAILED'}")
    print(f"    Ancestry 26:  {'PASSED' if rc_26 == 0 else 'FAILED'}")
    print(f"    Ancestry 27:  {'PASSED' if rc_27 == 0 else 'FAILED'}")
    print(f"    HEAD Commit:  {head_commit}")
    print(f"    Start Tag:    {start_commit} (matches v4: {commits_match})")
    print(f"    Branch:       {branch}")

    if not ancestry_ok:
        print("[!] Git ancestry check failed!")
        sys.exit(1)
    if not commits_match:
        print("[!] Start tag does not match stage-28a-complete-v4 (0e83898a1272ecd8af2fc93f607e694ca07954cf)!")
        sys.exit(1)

    print("[*] Snapshotting English dataset releases...")
    corpus_releases_dir = repo_root / "data" / "simplification_corpus" / "releases"
    dataset_snapshots = {}
    if corpus_releases_dir.exists():
        for release_ver in ["0.1.0", "0.2.0"]:
            rel_path = corpus_releases_dir / release_ver
            if rel_path.exists():
                dataset_snapshots[release_ver] = {}
                for fpath in rel_path.glob("**/*"):
                    if fpath.is_file():
                        rel_name = str(fpath.relative_to(rel_path)).replace("\\", "/")
                        dataset_snapshots[release_ver][rel_name] = compute_sha256(fpath)

    print(f"    Snapshotted {len(dataset_snapshots)} releases.")

    print("[*] Snapshotting Stage 28A manifest...")
    manifest_28a_path = repo_root / "docs" / "stage28a_manifest.sha256"
    manifest_28a_hash = compute_sha256(manifest_28a_path) if manifest_28a_path.exists() else None
    print(f"    stage28a_manifest.sha256: {manifest_28a_hash}")

    print("[*] Auditing database record counts (adaptive_learning.db)...")
    db_path = repo_root / "backend" / "adaptive_learning.db"
    db_info = {
        "exists": db_path.exists(),
        "path": "backend/adaptive_learning.db",
        "size_bytes": db_path.stat().st_size if db_path.exists() else 0,
        "tables": {}
    }

    if db_path.exists():
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]
        for t in sorted(tables):
            count = cur.execute(f"SELECT COUNT(*) FROM \"{t}\"").fetchone()[0]
            db_info["tables"][t] = count
        conn.close()
        print(f"    Found {len(db_info['tables'])} tables in adaptive_learning.db.")
    else:
        print("    [!] Warning: backend/adaptive_learning.db not found.")

    snapshot_data = {
        "stage": "Stage 29 WP0 Prerequisite Snapshot",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git": {
            "branch": branch,
            "head_commit": head_commit,
            "stage_29_start_commit": start_commit,
            "stage_28a_complete_v4_commit": v4_commit,
            "ancestry_verification": {
                "stage_28a_ancestor": rc_28a == 0,
                "stage_26_ancestor": rc_26 == 0,
                "stage_27_ancestor": rc_27 == 0
            }
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "node_version": run_cmd(["node", "--version"])[1] if run_cmd(["node", "--version"])[0] == 0 else "unknown"
        },
        "governed_dataset_releases": dataset_snapshots,
        "stage28a_manifest_sha256": manifest_28a_hash,
        "database_baseline": db_info
    }

    out_file = snapshot_dir / "prerequisite_snapshot.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2)

    print(f"[+] Prerequisite snapshot successfully written to: {out_file}")

if __name__ == "__main__":
    main()
