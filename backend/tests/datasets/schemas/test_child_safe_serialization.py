import os
import pytest
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository

def test_child_safe_views_never_contain_answers_in_either_mode():
    for mode in ["stage13_compat", "v1"]:
        os.environ["DATASET_SCHEMA_MODE"] = mode
        repo = AdaptationTestSetRepository()
        activities = repo.get_all_activities()
        assert len(activities) > 0

        for act in activities:
            child_view = repo.get_child_activity(act.activity_id)
            assert child_view is not None
            assert "protected" not in child_view
            assert "protected_answer" not in child_view
            assert "acceptable_answers" not in child_view
            assert "target_word" not in child_view
            assert "target_structure" not in child_view
            assert "scoring_rubric" not in child_view
