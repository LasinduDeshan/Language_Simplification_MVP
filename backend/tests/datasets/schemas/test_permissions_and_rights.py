import pytest
from app.datasets.common.metadata import RightsMetadata
from app.datasets.common.permissions import filter_child_safe_activity, can_process_with_external_api

def test_filter_child_safe_activity_removes_answers():
    activity_dict = {
        "activity_id": "C3-EN-VOC-0001",
        "original_instruction": "Look at the cat.",
        "protected_answer": "cat",
        "acceptable_answers": ["kitten", "feline"],
        "target_word": "cat",
        "scoring_rubric": {"rubric_key": "exact_match"}
    }
    
    child_view = filter_child_safe_activity(activity_dict)
    assert "activity_id" in child_view
    assert "original_instruction" in child_view
    assert "protected_answer" not in child_view
    assert "acceptable_answers" not in child_view
    assert "target_word" not in child_view
    assert "scoring_rubric" not in child_view

def test_external_api_processing_gating():
    default_rights = RightsMetadata()
    assert can_process_with_external_api(default_rights) is False

    allowed_rights = RightsMetadata(
        licence_id="custom-permission",
        external_api_processing_allowed=True
    )
    assert can_process_with_external_api(allowed_rights) is True
