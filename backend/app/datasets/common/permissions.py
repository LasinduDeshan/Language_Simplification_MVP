"""
Permission and privacy filtering utilities for Stage 14 datasets.
"""
from typing import Dict, Any
from app.datasets.common.metadata import RightsMetadata

CHILD_RESTRICTED_KEYS = {
    "protected",
    "protected_answer",
    "acceptable_answers",
    "target_word",
    "target_structure",
    "expected_concepts",
    "correct_answer",
    "scoring_rubric"
}

def filter_child_safe_activity(activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a child-safe representation of an activity by stripping all protected answer
    keys, answer elements, and internal evaluation rubrics.
    """
    child_view = {}
    for k, v in activity_data.items():
        if k not in CHILD_RESTRICTED_KEYS:
            child_view[k] = v
    return child_view

def can_process_with_external_api(rights: RightsMetadata) -> bool:
    """
    Determines if a record's rights permit transmission to external model/LLM APIs.
    """
    return bool(rights.external_api_processing_allowed)
