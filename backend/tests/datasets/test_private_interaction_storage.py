import os
import json
import pytest
from app.datasets.interaction_dataset.repository import InteractionDatasetRepository
from app.database.db import SessionLocal

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
GITIGNORE_FILE = os.path.join(BASE_DIR, ".gitignore")

def test_private_interaction_paths_are_gitignored():
    assert os.path.exists(GITIGNORE_FILE)
    with open(GITIGNORE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "data/interaction_dataset/private/" in content
    assert "data/interaction_dataset/deidentified_exports/" in content
    assert "data/interaction_dataset/research_releases/" in content

def test_database_is_operational_truth_for_interactions():
    repo = InteractionDatasetRepository()
    db = SessionLocal()
    try:
        interactions = repo.get_interactions(db, limit=10)
        assert isinstance(interactions, list)
        for item in interactions:
            assert item.schema_status == "draft_stage13"
            assert item.learner_id.startswith("CHILD-") or item.learner_id.startswith("PSEUDO-")
    finally:
        db.close()
