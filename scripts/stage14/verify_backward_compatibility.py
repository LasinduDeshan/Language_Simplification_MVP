"""
Verifies backward compatibility and schema mode switching between stage13_compat and v1.
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository

def verify_backward_compatibility():
    print("=== VERIFYING BACKWARD COMPATIBILITY & MODE SWITCHING ===")

    # 1. Test Mode: stage13_compat
    os.environ["DATASET_SCHEMA_MODE"] = "stage13_compat"
    repo_legacy = AdaptationTestSetRepository()
    legacy_activities = repo_legacy.get_all_activities()
    print(f"[OK] stage13_compat loaded {len(legacy_activities)} activities.")
    assert len(legacy_activities) == 40

    # 2. Test Mode: v1
    os.environ["DATASET_SCHEMA_MODE"] = "v1"
    repo_v1 = AdaptationTestSetRepository()
    v1_activities = repo_v1.get_all_activities()
    print(f"[OK] v1 mode loaded {len(v1_activities)} activities.")
    assert len(v1_activities) == 40

    # 3. Verify content equivalence
    for leg, v1 in zip(legacy_activities, v1_activities):
        assert leg.activity_id == v1.activity_id
        assert leg.original_instruction == v1.original_instruction

    # 4. Verify child safe protection in both modes
    for r in [repo_legacy, repo_v1]:
        sample = r.get_all_activities()[0]
        cv = r.get_child_activity(sample.activity_id)
        assert "protected_answer" not in cv
        assert "protected" not in cv
        assert "acceptable_answers" not in cv

    print("[OK] Backward compatibility and rollback capability verified successfully.")
    return True

if __name__ == "__main__":
    verify_backward_compatibility()
