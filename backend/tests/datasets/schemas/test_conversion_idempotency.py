import os
import hashlib
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

ADAPTATION_V1 = os.path.join(BASE_DIR, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
SIMPLIFICATION_V1 = os.path.join(BASE_DIR, "data", "simplification_corpus", "releases", "0.1.0", "simplification_corpus.json")
LEXICON_V1 = os.path.join(BASE_DIR, "data", "lexicons", "en", "releases", "0.1.0", "lexicon_repository.json")

def _compute_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def test_v1_files_have_stable_counts_and_valid_json():
    h_adapt = _compute_hash(ADAPTATION_V1)
    h_simp = _compute_hash(SIMPLIFICATION_V1)
    h_lex = _compute_hash(LEXICON_V1)

    assert len(h_adapt) == 64
    assert len(h_simp) == 64
    assert len(h_lex) == 64

    # Verify deterministic counts
    with open(ADAPTATION_V1, "r", encoding="utf-8") as f:
        assert len(json.load(f)) == 40
    with open(SIMPLIFICATION_V1, "r", encoding="utf-8") as f:
        assert len(json.load(f)) == 210
    with open(LEXICON_V1, "r", encoding="utf-8") as f:
        assert len(json.load(f)) == 18
