import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ADAPTATION_TASKS_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
SIMPLIFICATION_PAIRS_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")
LEXICON_FILE = os.path.join(BASE_DIR, "data", "lexicons", "en", "tiered_vocabulary_lexicon.json")

def verify_references():
    print("=== STAGE 13 CROSS-LAYER REFERENCE VERIFICATION ===")

    # 1. Load Adaptation Tasks
    with open(ADAPTATION_TASKS_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    task_ids = {t["activity_id"] for t in tasks}
    task_codes = {t["legacy_task_code"] for t in tasks if t.get("legacy_task_code")}

    print(f"Loaded {len(task_ids)} unique activity IDs in Adaptation Test Set.")

    # 2. Check Simplification Corpus references
    with open(SIMPLIFICATION_PAIRS_FILE, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    referenced_count = 0
    for p in pairs:
        src = p.get("source_activity_id")
        if src:
            referenced_count += 1
            # Check reference exists in task_ids or task_codes
            is_valid = (src in task_ids) or (src in task_codes) or any(src in tid for tid in task_ids)
            assert is_valid, f"Broken reference in corpus pair {p['pair_id']}: {src} not found in test set!"

    print(f"[OK] All {referenced_count} cross-layer activity references in Simplification Corpus are valid.")

    # 3. Check Lexicon validity
    with open(LEXICON_FILE, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
    assert len(lexicon) > 0, "Lexicon dictionary must not be empty"
    for item in lexicon:
        assert "word" in item and ("simple_alternative" in item or "simplified_alternatives" in item)
    print(f"[OK] Tiered vocabulary lexicon contains {len(lexicon)} validated lexical entries.")

    print("[OK] All cross-layer reference checks PASSED.")
    return True

if __name__ == "__main__":
    verify_references()
