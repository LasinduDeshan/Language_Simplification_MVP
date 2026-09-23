import pytest
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository

def test_child_activity_view_omits_protected_answers():
    repo = AdaptationTestSetRepository()
    activities = repo.get_all_activities()
    assert len(activities) > 0

    for act in activities:
        child_view = repo.get_child_activity(act.activity_id)
        assert child_view is not None
        assert "protected" not in child_view, f"Leakage: protected in child view for {act.activity_id}"
        assert "protected_answer" not in child_view, f"Leakage: protected_answer in child view for {act.activity_id}"
        assert "acceptable_answers" not in child_view, f"Leakage: acceptable_answers in child view for {act.activity_id}"
        assert "target_word" not in child_view, f"Leakage: target_word in child view for {act.activity_id}"
        assert "target_structure" not in child_view, f"Leakage: target_structure in child view for {act.activity_id}"
        assert "correct_answer" not in child_view, f"Leakage: correct_answer in child view for {act.activity_id}"

def test_full_activity_record_retains_authorized_evaluation_fields():
    repo = AdaptationTestSetRepository()
    activities = repo.get_all_activities()
    sample = activities[0]
    full_rec = repo.get_full_activity_record(sample.activity_id)
    assert full_rec is not None
    # Authorized record contains the answer keys (either in protected block or as attributes)
    has_answer = hasattr(full_rec, "protected") or hasattr(full_rec, "protected_answer")
    assert has_answer
