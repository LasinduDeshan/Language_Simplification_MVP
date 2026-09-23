import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ADAPTATION_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
SIMPLIFICATION_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")
INTERACTION_FILE = os.path.join(BASE_DIR, "data", "interaction_dataset", "private", "private_interactions_snapshot.json")

def test_layer_files_are_physically_separated():
    assert os.path.exists(ADAPTATION_FILE), "Adaptation test set file must exist in separate directory"
    assert os.path.exists(SIMPLIFICATION_FILE), "Simplification corpus file must exist in separate directory"
    assert os.path.exists(INTERACTION_FILE), "Interaction snapshot must exist in private directory"

def test_adaptation_records_do_not_contain_runtime_learner_evidence():
    with open(ADAPTATION_FILE, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    for t in tasks:
        assert "learner_id" not in t, "Learner ID found in Adaptation Test Set!"
        assert "session_id" not in t, "Session ID found in Adaptation Test Set!"
        assert "child_response" not in t, "Child response found in Adaptation Test Set!"

def test_simplification_pairs_do_not_contain_runtime_learner_evaluations():
    with open(SIMPLIFICATION_FILE, "r", encoding="utf-8") as f:
        pairs = json.load(f)
    for p in pairs:
        assert "learner_id" not in p, "Learner ID found in Simplification Corpus!"
        assert "is_correct" not in p, "Learner scoring found in Simplification Corpus!"

def test_interaction_records_contain_learner_evidence_only():
    with open(INTERACTION_FILE, "r", encoding="utf-8") as f:
        interactions = json.load(f)
    for i in interactions:
        assert "learner_id" in i
        assert "activity_id" in i
        assert "attempt_number" in i
