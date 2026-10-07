"""
Unit tests for Dataset Adapters (SourceItemAdapter, SimplificationPairAdapter, AdaptationActivityAdapter, LexiconEntryAdapter)
"""
from app.nlp_preprocessing.schemas import (
    SourceItemAdapter,
    SimplificationPairAdapter,
    AdaptationActivityAdapter,
    LexiconEntryAdapter
)

def test_source_item_adapter():
    raw_src = {
        "source_item_id": "SRC-VOC-0101",
        "original_text": "Point to the red apple.",
        "primary_domain": "vocabulary",
        "dataset_split": "development_candidate_train",
        "protected_meaning_units": ["red apple"]
    }
    instances = SourceItemAdapter.extract_text_instances(raw_src)
    assert len(instances) == 1
    assert instances[0].text_instance_id == "SRC-VOC-0101__SRC"
    assert instances[0].text_role == "source_text"
    assert instances[0].text == "Point to the red apple."

def test_simplification_pair_adapter():
    raw_pair = {
        "pair_id": "SIMP-EN-000301",
        "source_item_id": "SRC-VOC-0101",
        "original_text": "Point to the red apple on the wooden desk.",
        "simplified_text": "Look at the desk. Tap the red apple.",
        "support_level": "moderate",
        "dataset_split": "development_candidate_train",
        "protected_meaning_units": ["red apple", "desk"]
    }
    instances = SimplificationPairAdapter.extract_text_instances(raw_pair)
    assert len(instances) == 2
    assert instances[0].text_role == "source_text"
    assert instances[1].text_role == "simplified_text"
    assert instances[1].text_instance_id == "SIMP-EN-000301__SIMP"

def test_adaptation_activity_adapter():
    raw_act = {
        "activity_id": "C3-EN-VOC-0101",
        "source_item_id": "SRC-VOC-0101",
        "original_instruction": "Identify the depicted red apple.",
        "child_friendly_instruction": "Point to the apple.",
        "expected_response": "apple"
    }
    instances = AdaptationActivityAdapter.extract_text_instances(raw_act)
    assert len(instances) == 2
    assert instances[0].text_role == "activity_instruction"
    assert instances[1].text_role == "activity_prompt"
    assert instances[0].protected_answer_ref == "C3-EN-VOC-0101__ANSWER"

def test_lexicon_entry_adapter():
    raw_lex = {
        "lexicon_id": "LEX-EN-000101",
        "headword": "enormous",
        "child_definition": "very, very big",
        "example_sentence": "An elephant is an enormous animal."
    }
    instances = LexiconEntryAdapter.extract_text_instances(raw_lex)
    assert len(instances) == 2
    assert instances[0].text_role == "lexicon_definition"
    assert instances[1].text_role == "lexicon_example"
