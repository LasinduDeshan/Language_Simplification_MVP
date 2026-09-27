"""
End-to-End integration test for Stage 20 expansion workflow.
"""
import pytest
import os
import tempfile
from app.datasets.expansion.authoring_validator import AuthoringValidator
from app.datasets.expansion.duplicate_detector import DuplicateDetector
from app.datasets.expansion.meaning_validator import MeaningValidator
from app.datasets.expansion.split_builder import SplitBuilder
from app.datasets.expansion.leakage_detector import LeakageDetector
from app.datasets.expansion.release_builder import ReleaseBuilder

def test_stage20_end_to_end_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Author pilot item
        src_item = {
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
                "batch_id": "STAGE20-BATCH-PILOT",
                "revision_id": "REV-001"
            }
        }
        
        pairs = [
            {
                "pair_id": "SIMP-EN-000001",
                "source_item_id": "SRC-EN-VOC-0001",
                "schema_version": "1.0.0",
                "dataset_version": "0.2.0",
                "language": "en",
                "support_level": "mild",
                "original_text": "Identify the cat.",
                "simplified_text": "Find the cat.",
                "protected_meaning_units": ["cat"],
                "quality_status": "automatic_check_passed",
                "provenance": src_item["provenance"]
            },
            {
                "pair_id": "SIMP-EN-000002",
                "source_item_id": "SRC-EN-VOC-0001",
                "schema_version": "1.0.0",
                "dataset_version": "0.2.0",
                "language": "en",
                "support_level": "moderate",
                "original_text": "Identify the cat.",
                "simplified_text": "Look at the picture. Point to the cat.",
                "protected_meaning_units": ["cat"],
                "quality_status": "automatic_check_passed",
                "provenance": src_item["provenance"]
            },
            {
                "pair_id": "SIMP-EN-000003",
                "source_item_id": "SRC-EN-VOC-0001",
                "schema_version": "1.0.0",
                "dataset_version": "0.2.0",
                "language": "en",
                "support_level": "strong",
                "original_text": "Identify the cat.",
                "simplified_text": "1. Look here.\n2. Tap the cat.",
                "protected_meaning_units": ["cat"],
                "quality_status": "automatic_check_passed",
                "provenance": src_item["provenance"]
            }
        ]
        
        # 2. Schema validation
        validator = AuthoringValidator()
        v_res = validator.validate_batch({"batch_id": "PILOT", "source_items": [src_item], "simplification_pairs": pairs})
        assert v_res["is_schema_valid"] is True

        # 3. Duplicate check
        dup = DuplicateDetector()
        d_res = dup.scan_records([src_item])
        assert d_res["is_unique"] is True

        # 4. Meaning validation
        m_val = MeaningValidator()
        for p in pairs:
            m_res = m_val.validate_meaning_units(p["original_text"], p["simplified_text"], p["protected_meaning_units"])
            assert m_res["is_preserved"] is True

        # 5. Group splitting
        splitter = SplitBuilder(seed=42)
        eligible, _ = splitter.filter_candidate_eligibility(pairs)
        splits = splitter.build_group_aware_splits(eligible)
        
        # 6. Leakage check
        leak = LeakageDetector()
        l_res = leak.check_split_containment(splits)
        assert l_res["is_clean"] is True

        # 7. Release building
        builder = ReleaseBuilder(root_dir=tmpdir, dataset_version="0.2.0")
        builder.build_release_staging(
            adaptation_activities=[],
            simplification_pairs=pairs,
            splits=splits,
            lexicon_entries=[],
            locked_test_manifest={"manifest_type": "locked"}
        )
        pub = builder.publish_release(dry_run=False)
        assert pub["status"] == "published_successfully"
