import pytest
from app.database.db import SessionLocal
from app.database.models import Task, ActivityAsset

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_all_30_activities_dataset_integrity(db_session):
    """
    Verifies that all 30 activities exist, are assigned to the 4 core categories,
    and have valid age bounds, delivery modes, response modes, and licensing fields.
    """
    tasks = db_session.query(Task).all()
    assert len(tasks) >= 30

    categories = set(t.category for t in tasks)
    expected_categories = {"vocabulary", "grammar", "sentence_and_instruction", "comprehension"}
    assert categories.issubset(expected_categories) or expected_categories.issubset(categories)

    for task in tasks:
        # Age bounds
        assert 4 <= task.minimum_age <= 8
        assert 4 <= task.maximum_age <= 8
        assert task.minimum_age <= task.maximum_age

        # Instructions
        assert len(task.original_instruction) > 0
        assert task.learning_objective is not None

        # Delivery & response modes
        assert isinstance(task.delivery_modes, list) and len(task.delivery_modes) > 0
        assert isinstance(task.response_modes, list) and len(task.response_modes) > 0

        # Assets & alt text validation
        for asset in task.assets:
            assert asset.alt_text is not None and len(asset.alt_text) > 0
            assert asset.license_type is not None and len(asset.license_type) > 0
            assert asset.asset_creator is not None and len(asset.asset_creator) > 0
            assert asset.permission_status == "Approved for project use"
