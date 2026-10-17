"""
Immutability and database isolation verification tests for Stage 36 (WP9).
"""

import hashlib
from pathlib import Path
import subprocess
import pytest

BASELINE_DB_SHA256 = "44ff4f07fca1ac92343875bb8c82957df5cc721017dd08d20e901689392bb701"
EXPECTED_STAGE35_V7_COMMIT = "cd86a6b0aff2d07d7d0c4f8079f10e9833b5b3d0"
EXPECTED_STAGE35_V6_COMMIT = "f222efc5919627effd62fa2b31c14f5913b6ec9e"


class TestStage36ImmutabilityAndIsolation:
    def test_database_baseline_integrity(self):
        backend_root = Path(__file__).resolve().parents[2]
        db_path = backend_root / "adaptive_learning.db"

        assert db_path.exists(), f"adaptive_learning.db missing at {db_path}"
        with open(db_path, "rb") as f:
            actual_sha256 = hashlib.sha256(f.read()).hexdigest()

        assert actual_sha256 == BASELINE_DB_SHA256, (
            f"Database integrity violated! Expected {BASELINE_DB_SHA256}, got {actual_sha256}"
        )

    def test_historical_tags_immutability(self):
        repo_root = Path(__file__).resolve().parents[3]

        def get_tag_commit(tag: str) -> str:
            res = subprocess.run(
                ["git", "rev-parse", f"{tag}^{{commit}}"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()

        v6_commit = get_tag_commit("stage-35-complete-v6")
        assert v6_commit == EXPECTED_STAGE35_V6_COMMIT, (
            f"stage-35-complete-v6 altered! Expected {EXPECTED_STAGE35_V6_COMMIT}, got {v6_commit}"
        )

        v7_commit = get_tag_commit("stage-35-complete-v7")
        assert v7_commit == EXPECTED_STAGE35_V7_COMMIT, (
            f"stage-35-complete-v7 altered! Expected {EXPECTED_STAGE35_V7_COMMIT}, got {v7_commit}"
        )

        start_commit = get_tag_commit("stage-36-start")
        assert start_commit == EXPECTED_STAGE35_V7_COMMIT, (
            f"stage-36-start altered! Expected {EXPECTED_STAGE35_V7_COMMIT}, got {start_commit}"
        )
