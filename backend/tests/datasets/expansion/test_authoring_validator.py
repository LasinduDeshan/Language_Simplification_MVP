"""
Unit tests for Stage 20 Authoring Validator.
"""
import pytest
from app.datasets.expansion.authoring_validator import AuthoringValidator

def test_authoring_validator_valid_batch():
    validator = AuthoringValidator()
    valid_batch = {
        "batch_id": "TEST-BATCH-01",
        "source_items": [
            {
                "source_item_id": "SRC-EN-VOC-0001",
                "schema_version": "1.0.0",
                "dataset_version": "0.2.0",
                "language": "en",
                "age_min": 4,
                "age_max": 6,
                "primary_domain": "vocabulary",
                "content_type": "naming",
                "source_difficulty": "easy",
                "original_text": "Identify the cat.",
                "protected_meaning_units": ["cat"],
                "expected_response_mode": "action",
                "source_type": "team_authored",
                "validation_status": "draft",
                "research_eligible": False,
                "approved_for_child_delivery": False,
                "requires_expert_review": True,
                "provenance": {
                    "authoring_method": "human_authored",
                    "created_by": "test_user",
                    "batch_id": "TEST-BATCH-01",
                    "revision_id": "REV-001"
                }
            }
        ]
    }
    res = validator.validate_batch(valid_batch)
    assert res["is_schema_valid"] is True
    assert res["total_valid"] == 1
    assert res["failed_count"] == 0

def test_authoring_validator_circ_lexicon():
    validator = AuthoringValidator()
    batch = {
        "batch_id": "TEST-BATCH-CIRC",
        "lexicon_entries": [
            {
                "lexicon_id": "LEX-EN-000001",
                "schema_version": "1.0.0",
                "dataset_version": "0.2.0",
                "language": "en",
                "headword": "big",
                "normalized_form": "big",
                "pos": "adj",
                "sense_id": "sense_1",
                "age_min": 4,
                "age_max": 6,
                "difficulty_tier": "easy",
                "simple_replacement": "big",
                "child_definition": "not small",
                "example_sentence": "The dog is big.",
                "provenance": {
                    "authoring_method": "human_authored",
                    "created_by": "test_user",
                    "batch_id": "TEST-BATCH-CIRC",
                    "revision_id": "REV-001"
                }
            }
        ]
    }
    res = validator.validate_batch(batch)
    assert res["review_count"] >= 1
    assert "Self-referential" in res["review_records"][0]["reason"]
