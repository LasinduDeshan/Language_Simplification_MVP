"""
Converts Stage 13 Simplification Corpus pairs into V1 Pydantic models and atomically publishes release 0.1.0.
All 210 pairs strictly remain draft, research_eligible=False, approved_for_child_delivery=False.
"""
import os
import sys
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.simplification_corpus.schemas import SimplificationPairV1
from app.datasets.common.enums import (
    LanguageCode, SupportLevel, DifficultyLevel, ContentType,
    SourceType, ValidationStatus, ResearchEligibilityStatus
)
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata, ReviewBlock

SOURCE_FILE = os.path.join(BASE_DIR, "data", "simplification_corpus", "en", "draft", "draft_pairs.json")
RELEASE_DIR = os.path.join(BASE_DIR, "data", "simplification_corpus", "releases", "0.1.0")

def convert_simplification_pairs():
    print(f"=== CONVERTING SIMPLIFICATION CORPUS TO V1 (RELEASE 0.1.0) ===")
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw_pairs = json.load(f)

    v1_pairs = []
    for raw in raw_pairs:
        pair_id = raw["pair_id"]
        
        # Support level mapping
        sup_str = raw.get("support_level", "moderate")
        sup = SupportLevel(sup_str if sup_str in ["mild", "moderate", "strong"] else "moderate")

        # Source type mapping
        src_type_str = raw.get("source_type", "team_authored")
        if src_type_str == "adaptation_engine_generated":
            src_type = SourceType.GENERATED
        else:
            src_type = SourceType.TEAM_AUTHORED

        pair = SimplificationPairV1(
            pair_id=pair_id,
            source_activity_id=raw.get("source_activity_id"),
            schema_version="1.0.0",
            dataset_version="0.1.0",
            language=LanguageCode.EN,
            content_type=ContentType.INSTRUCTION,
            original_text=raw["original_text"],
            simplified_text=raw["simplified_text"],
            support_level=sup,
            age_min=raw.get("age_min", 4),
            age_max=raw.get("age_max", 8),
            original_difficulty=DifficultyLevel.MEDIUM,
            simplified_difficulty=DifficultyLevel.EASY,
            operations=raw.get("operations", []),
            protected_meaning_units=raw.get("protected_meaning_units", []),
            review=ReviewBlock(),  # Unreviewed draft
            source=SourceMetadata(
                source_type=src_type,
                source_name="Component 3 English MVP Simplification Corpus",
                source_record_id=raw.get("source_activity_id"),
                created_by_role="project_team"
            ),
            rights=RightsMetadata(
                licence_id="project-internal",
                redistribution_allowed=False,
                commercial_use_allowed=False,
                external_api_processing_allowed=False
            ),
            governance=GovernanceMetadata(
                validation_status=ValidationStatus.DRAFT,
                research_eligibility_status=ResearchEligibilityStatus.NOT_ASSESSED,
                research_eligible=False,
                approved_for_child_delivery=False,
                is_simulated=False,
                contains_personal_data=False
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        v1_pairs.append(pair)

    # Validate all through Pydantic
    serialized = [p.model_dump(mode="json") for p in v1_pairs]
    
    # Atomic staging
    os.makedirs(RELEASE_DIR, exist_ok=True)
    staging_file = os.path.join(RELEASE_DIR, ".staging_simplification_corpus.json")
    target_file = os.path.join(RELEASE_DIR, "simplification_corpus.json")

    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2)

    shutil.move(staging_file, target_file)
    print(f"[OK] Atomically published {len(v1_pairs)} V1 simplification pairs to {target_file}")
    return len(v1_pairs)

if __name__ == "__main__":
    convert_simplification_pairs()
