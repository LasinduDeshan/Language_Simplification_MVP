"""
Snapshots Stage 13 baseline data counts and paths before Stage 14 v1 conversion.
"""
import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

STAGE13_ADAPTATION_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
STAGE13_SIMPLIFICATION_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")
STAGE13_LEXICON_FILE = os.path.join(BASE_DIR, "data", "lexicons", "en", "tiered_vocabulary_lexicon.json")

def snapshot_stage13():
    print("=== RECORDING STAGE 13 BASELINE SNAPSHOT ===")
    
    with open(STAGE13_ADAPTATION_FILE, "r", encoding="utf-8") as f:
        adaptations = json.load(f)
    with open(STAGE13_SIMPLIFICATION_FILE, "r", encoding="utf-8") as f:
        pairs = json.load(f)
    with open(STAGE13_LEXICON_FILE, "r", encoding="utf-8") as f:
        lexicon = json.load(f)

    snapshot = {
        "stage13_baseline_tag": "stage-13-complete",
        "adaptation_activities_count": len(adaptations),
        "simplification_pairs_count": len(pairs),
        "lexicon_entries_count": len(lexicon),
        "total_source_reusable_records": len(adaptations) + len(pairs) + len(lexicon)
    }

    print(f"Stage 13 Baseline: {snapshot}")
    return snapshot

if __name__ == "__main__":
    snapshot_stage13()
