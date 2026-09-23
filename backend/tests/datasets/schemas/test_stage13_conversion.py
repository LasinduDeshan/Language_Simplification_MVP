import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

ADAPTATION_V1 = os.path.join(BASE_DIR, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
SIMPLIFICATION_V1 = os.path.join(BASE_DIR, "data", "simplification_corpus", "releases", "0.1.0", "simplification_corpus.json")
LEXICON_V1 = os.path.join(BASE_DIR, "data", "lexicons", "en", "releases", "0.1.0", "lexicon_repository.json")

def test_stage13_converted_files_exist_and_match_counts():
    assert os.path.exists(ADAPTATION_V1)
    assert os.path.exists(SIMPLIFICATION_V1)
    assert os.path.exists(LEXICON_V1)

    with open(ADAPTATION_V1, "r", encoding="utf-8") as f:
        adaptations = json.load(f)
    assert len(adaptations) == 40

    with open(SIMPLIFICATION_V1, "r", encoding="utf-8") as f:
        pairs = json.load(f)
    assert len(pairs) == 210

    with open(LEXICON_V1, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
    assert len(lexicon) == 18

def test_all_210_pairs_remain_draft_and_ineligible():
    with open(SIMPLIFICATION_V1, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    for p in pairs:
        gov = p["governance"]
        assert gov["validation_status"] == "draft"
        assert gov["research_eligible"] is False
        assert gov["approved_for_child_delivery"] is False
        assert p["language"] == "en"

def test_no_external_or_sinhala_records():
    with open(ADAPTATION_V1, "r", encoding="utf-8") as f:
        adaptations = json.load(f)
    for a in adaptations:
        assert a["language"] == "en"
        assert "si" not in a["language"]
        assert "ASSET" not in a.get("activity_id", "")
        assert "WikiLarge" not in a.get("activity_id", "")
