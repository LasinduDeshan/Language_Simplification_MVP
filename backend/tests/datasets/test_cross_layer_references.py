import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ADAPTATION_TASKS_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
SIMPLIFICATION_PAIRS_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")

def test_simplification_pairs_cross_layer_references():
    with open(ADAPTATION_TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    task_ids = {t["activity_id"] for t in tasks}
    task_codes = {t["legacy_task_code"] for t in tasks if t.get("legacy_task_code")}

    with open(SIMPLIFICATION_PAIRS_FILE, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    for p in pairs:
        src = p.get("source_activity_id")
        if src:
            is_valid = (src in task_ids) or (src in task_codes) or any(src in tid for tid in task_ids)
            assert is_valid, f"Corpus pair {p['pair_id']} references unknown activity {src}"
