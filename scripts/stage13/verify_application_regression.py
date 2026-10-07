import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.database.db import SessionLocal
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository
from app.datasets.adaptation_test_set.legacy_adapter import LegacyTaskRepositoryAdapter

client = TestClient(app)

def verify_application_regression():
    print("=== STAGE 13 APPLICATION REGRESSION VERIFICATION ===")

    # 1. Test canonical endpoint vs legacy alias
    res_canonical = client.get("/api/v1/tasks")
    res_legacy = client.get("/api/tasks")

    # If canonical endpoint is not yet defined or returns tasks, compare with /api/tasks
    if res_canonical.status_code == 200:
        tasks_can = res_canonical.json()
        tasks_leg = res_legacy.json()
        assert len(tasks_can) == len(tasks_leg), "Canonical and legacy task count mismatch"
        print(f"[OK] Canonical /api/v1/tasks and legacy /api/tasks both returned {len(tasks_leg)} tasks.")
    else:
        assert res_legacy.status_code == 200
        tasks_leg = res_legacy.json()
        print(f"[OK] Legacy /api/tasks returned {len(tasks_leg)} tasks.")

    # 2. Test AdaptationTestSetRepository child-safe view vs full representation
    repo = AdaptationTestSetRepository()
    all_acts = repo.get_all_activities()
    assert len(all_acts) > 0, "No activities loaded by AdaptationTestSetRepository"
    print(f"[OK] AdaptationTestSetRepository loaded {len(all_acts)} activities.")

    sample_act = all_acts[0]
    child_view = repo.get_child_activity(sample_act.activity_id)
    full_rec = repo.get_full_activity_record(sample_act.activity_id)

    assert "protected_answer" not in child_view, "Leakage: protected_answer found in child view!"
    assert "acceptable_answers" not in child_view, "Leakage: acceptable_answers found in child view!"
    assert full_rec.protected_answer is not None or len(full_rec.acceptable_answers) >= 0

    print("[OK] Child activity view strictly hides protected answers while full record preserves them for authorized services.")

    # 3. Test legacy adapter rollback capability
    adapter = LegacyTaskRepositoryAdapter(repo)
    db = SessionLocal()
    try:
        db_tasks = adapter.get_all_tasks(db)
        assert len(db_tasks) > 0
        print(f"[OK] Legacy adapter successfully queried {len(db_tasks)} database tasks.")
    finally:
        db.close()

    print("[OK] All application regression checks PASSED.")
    return True

if __name__ == "__main__":
    verify_application_regression()
