"""
Stage 34 — Locked-Test Protocol and Upstream Immutability Verifier (WP9)
Verifies:
1. Stage 33 rules and configurations remain 100% byte-identical (zero modification);
2. Locked-test partition items were evaluated under blinded conditions without leakage;
3. Child welfare / non-clinical flags remain strictly enforced (approved_for_child_delivery == False).
"""

import hashlib
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SNAPSHOT_FILE = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "snapshots" / "stage33_prerequisite_snapshot.json"
CONFIG_FILE = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "registry" / "stage34_configuration.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_locked_test_and_immutability():
    print("=== Stage 34 Locked-Test Protocol and Immutability Verification ===")

    assert SNAPSHOT_FILE.exists(), f"Missing snapshot: {SNAPSHOT_FILE}"
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    # 1. Verify upstream Stage 33 file immutability
    simplification_hashes = snapshot["verified_hashes"]["simplification"]
    mismatches = []
    for rel_path, expected_hash in simplification_hashes.items():
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            mismatches.append(f"MISSING: {rel_path}")
            continue
        actual_hash = sha256_file(full_path)
        if actual_hash != expected_hash:
            mismatches.append(f"HASH MISMATCH on {rel_path}: expected {expected_hash}, got {actual_hash}")

    if mismatches:
        for m in mismatches:
            print(f"FAILED: {m}")
        return False

    print(f"Verified {len(simplification_hashes)} upstream Stage 33 files: ALL BYTE-IDENTICAL (0 modified).")

    # 2. Verify locked-test partition isolation
    # Check that locked-test items are present in assignment ledger and evaluated blindly
    assignment_file = PROJECT_ROOT / "data" / "sinhala_expert_validation" / "assignments" / "assignment_ledger.jsonl"
    with open(assignment_file, "r", encoding="utf-8") as f:
        assignments = [json.loads(line) for line in f if line.strip()]

    # From canonical analytical corpus, determine locked test item IDs
    corpus_file = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
    locked_test_item_ids = set()
    with open(corpus_file, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if line.strip():
                item = json.loads(line)
                if item.get("split") == "locked_test":
                    locked_test_item_ids.add(f"ITEM-S34-{idx:06d}")

    assert len(locked_test_item_ids) == 13, f"Expected 13 locked test items, got {len(locked_test_item_ids)}"
    locked_test_assignments = [a for a in assignments if a["item_id"] in locked_test_item_ids]
    assert len(locked_test_assignments) == 13 * 4, f"Expected 52 assignments for locked test, got {len(locked_test_assignments)}"

    # Confirm blinding: assignments do not disclose partition or rule ID
    for a in locked_test_assignments:
        assert "partition" not in a, f"Assignment {a['assignment_id']} leaks partition"
        assert "applied_rule_ids" not in a, f"Assignment {a['assignment_id']} leaks rule IDs"

    print("Verified 13 locked-test items: 52 blinded assignments, zero partition leakage.")

    # 3. Verify non-clinical and child safety delivery flags
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    flags = config["flags"]
    assert flags["approved_for_child_delivery"] is False, "approved_for_child_delivery must be False"
    assert flags["approved_for_unsupervised_child_delivery"] is False, "approved_for_unsupervised_child_delivery must be False"
    assert flags["requires_expert_review"] is True, "requires_expert_review must be True"

    print("Verified governance flags: approved_for_child_delivery == False (LOCKED).")
    print("VERIFICATION SUCCESS: Locked-test protocol and immutability invariants satisfied.")
    return True


if __name__ == "__main__":
    if not verify_locked_test_and_immutability():
        sys.exit(1)
