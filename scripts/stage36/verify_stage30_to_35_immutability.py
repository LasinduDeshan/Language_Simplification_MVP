"""
Verification script for Stage 30-35 immutability and database baseline preservation.
"""

import hashlib
from pathlib import Path
import subprocess

BASELINE_DB_SHA256 = "44ff4f07fca1ac92343875bb8c82957df5cc721017dd08d20e901689392bb701"
EXPECTED_TAGS = {
    "stage-35-complete-v6": "f222efc5919627effd62fa2b31c14f5913b6ec9e",
    "stage-35-complete-v7": "cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0",
    "stage-36-start": "cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0",
}


def verify_immutability():
    repo_root = Path(__file__).resolve().parents[2]
    db_path = repo_root / "backend" / "adaptive_learning.db"

    assert db_path.exists(), f"adaptive_learning.db missing at {db_path}"
    with open(db_path, "rb") as f:
        actual_sha256 = hashlib.sha256(f.read()).hexdigest()

    assert actual_sha256 == BASELINE_DB_SHA256, (
        f"Database baseline violated! Expected {BASELINE_DB_SHA256}, got {actual_sha256}"
    )
    print("PASS: backend/adaptive_learning.db matches baseline SHA-256 byte-for-byte.")

    for tag, expected_commit in EXPECTED_TAGS.items():
        res = subprocess.run(
            ["git", "rev-parse", f"{tag}^{{commit}}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        actual_commit = res.stdout.strip()
        assert actual_commit == expected_commit, (
            f"Tag {tag} altered! Expected {expected_commit}, got {actual_commit}"
        )
        print(f"PASS: Tag {tag} immutably points to {actual_commit}.")


if __name__ == "__main__":
    verify_immutability()
