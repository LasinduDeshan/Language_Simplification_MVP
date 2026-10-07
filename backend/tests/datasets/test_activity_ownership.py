import os
import pytest
from app.datasets.common.ownership import (
    is_component3_owner,
    get_layer_owner,
    DATASET_OWNERSHIP_MATRIX
)
from app.datasets.adaptation_test_set.repository import AdaptationTestSetRepository

def test_component3_does_not_own_production_activity_bank():
    # Production Activity Bank is owned by upstream Component 2 / Curriculum Authoring
    assert not is_component3_owner("production_activity_bank")
    assert DATASET_OWNERSHIP_MATRIX["production_activity_bank"]["canonical_owner"] == "Component 2 (AR) / Curriculum Authoring"

def test_component3_owns_adaptation_test_set_and_simplification_corpus():
    assert is_component3_owner("adaptation_test_set")
    assert is_component3_owner("simplification_corpus")

def test_adaptation_test_set_identifies_as_local_test_samples():
    repo = AdaptationTestSetRepository()
    activities = repo.get_all_activities()
    assert len(activities) > 0
    for act in activities:
        owner_val = act.activity_owner.value if hasattr(act.activity_owner, "value") else act.activity_owner
        assert owner_val in {"component_3", "component_3_language", "component_2_ar", "component_1"}
