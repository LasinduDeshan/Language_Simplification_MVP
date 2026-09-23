import os
import pytest
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository

def test_schema_mode_switching_and_content_parity():
    # 1. stage13_compat mode
    os.environ["DATASET_SCHEMA_MODE"] = "stage13_compat"
    repo_legacy = AdaptationTestSetRepository()
    legacy_tasks = repo_legacy.get_all_activities()
    assert len(legacy_tasks) == 40

    # 2. v1 mode
    os.environ["DATASET_SCHEMA_MODE"] = "v1"
    repo_v1 = AdaptationTestSetRepository()
    v1_tasks = repo_v1.get_all_activities()
    assert len(v1_tasks) == 40

    # 3. ID parity check
    legacy_ids = {t.activity_id for t in legacy_tasks}
    v1_ids = {t.activity_id for t in v1_tasks}
    assert legacy_ids == v1_ids
