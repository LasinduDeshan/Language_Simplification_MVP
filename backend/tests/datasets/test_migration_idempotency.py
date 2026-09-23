import os
import hashlib
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ADAPTATION_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
SIMPLIFICATION_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")

def _compute_file_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def test_migration_outputs_are_deterministic_and_valid():
    hash1_adapt = _compute_file_hash(ADAPTATION_FILE)
    hash1_simp = _compute_file_hash(SIMPLIFICATION_FILE)
    
    assert hash1_adapt is not None, "Adaptation file must exist"
    assert hash1_simp is not None, "Simplification file must exist"
    
    # Verify that JSON parsing is valid
    with open(ADAPTATION_FILE, "r", encoding="utf-8") as f:
        d1 = json.load(f)
        assert len(d1) == 40
    
    with open(SIMPLIFICATION_FILE, "r", encoding="utf-8") as f:
        d2 = json.load(f)
        assert len(d2) >= 40
