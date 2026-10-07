"""
Unit tests for Answer Data Protection & Sanitization
Ensures sensitive target answers are stored strictly as references/hashes and never leak as raw text in extracted TextInstance objects.
"""
from app.nlp_preprocessing.schemas import AdaptationActivityAdapter

def test_adaptation_activity_adapter_hides_raw_answer():
    activity_record = {
        "activity_id": "ACT-101",
        "source_item_id": "SRC-101",
        "original_instruction": "Select the primary color from the list.",
        "child_friendly_instruction": "Pick the main color.",
        "expected_response": "Yellow",
        "protected_answer": "Yellow",
        "dataset_split": "development_candidate_train",
        "provenance": {"source": "expert"}
    }
    
    instances = AdaptationActivityAdapter.extract_text_instances(activity_record)
    
    # Must extract instruction and prompt
    assert len(instances) == 2
    for inst in instances:
        assert inst.text != "Yellow"
        assert inst.protected_answer_ref == "ACT-101__ANSWER"
        assert "Yellow" not in inst.text
