"""
Converts Stage 13 Adaptation Test Set activities into V1 Pydantic models and atomically publishes release 0.1.0.
"""
import os
import sys
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.adaptation_test_set.schemas import AdaptationRecordV1, ProtectedElements
from app.datasets.common.enums import (
    LanguageCode, ActivityOwner, PrimaryDomain, DifficultyLevel, AdaptationPolicy,
    SourceType, ValidationStatus, ResearchEligibilityStatus
)
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata

SOURCE_FILE = os.path.join(BASE_DIR, "data", "adaptation_test_set", "en", "component3_local_samples", "c3_local_tasks.json")
RELEASE_DIR = os.path.join(BASE_DIR, "data", "adaptation_test_set", "releases", "0.1.0")

def convert_adaptation_records():
    print(f"=== CONVERTING ADAPTATION TEST SET TO V1 (RELEASE 0.1.0) ===")
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw_tasks = json.load(f)

    v1_records = []
    for raw in raw_tasks:
        activity_id = raw["activity_id"]
        
        # Domain mapping
        domain_str = raw.get("primary_domain", "vocabulary")
        if domain_str == "sentence_and_instruction":
            domain = PrimaryDomain.GRAMMAR
        else:
            domain = PrimaryDomain(domain_str)

        # Owner mapping
        owner_str = raw.get("activity_owner", "component_3")
        if "1" in owner_str:
            owner = ActivityOwner.COMPONENT_1
        elif "2" in owner_str:
            owner = ActivityOwner.COMPONENT_2_AR
        else:
            owner = ActivityOwner.COMPONENT_3_LANGUAGE

        # Protected elements
        protected = ProtectedElements(
            answer=raw.get("protected_answer"),
            elements=raw.get("protected_elements", []),
            target_skill_locked=True,
            acceptable_answers=raw.get("acceptable_answers", [])
        )

        record = AdaptationRecordV1(
            activity_id=activity_id,
            schema_version="1.0.0",
            dataset_version="0.1.0",
            activity_owner=owner,
            language=LanguageCode.EN,
            activity_type=raw.get("activity_type", "standard"),
            primary_domain=domain,
            target_skill=raw.get("target_skill"),
            age_min=raw.get("age_min", 4),
            age_max=raw.get("age_max", 8),
            difficulty=DifficultyLevel(raw.get("base_difficulty", "medium")),
            original_instruction=raw["original_instruction"],
            child_friendly_instruction=raw.get("child_friendly_instruction"),
            stimulus=raw.get("stimulus"),
            options=raw.get("options"),
            passage=raw.get("passage"),
            protected=protected,
            adaptation_policy=AdaptationPolicy(raw.get("adaptation_policy", "instruction_only")),
            allowed_transformations=raw.get("allowed_transformations", ["simplify_instruction", "add_audio"]),
            forbidden_transformations=raw.get("forbidden_transformations", ["change_stimulus", "expose_answer", "change_target_skill"]),
            source=SourceMetadata(
                source_type=SourceType.TEAM_AUTHORED,
                source_name="Component 3 English MVP Test Set",
                source_record_id=raw.get("legacy_task_code") or activity_id,
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
                is_simulated=True,
                contains_personal_data=False
            ),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        v1_records.append(record)

    # Validate all through Pydantic
    serialized = [r.model_dump(mode="json") for r in v1_records]
    
    # Atomic staging
    os.makedirs(RELEASE_DIR, exist_ok=True)
    staging_file = os.path.join(RELEASE_DIR, ".staging_adaptation_test_set.json")
    target_file = os.path.join(RELEASE_DIR, "adaptation_test_set.json")

    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2)

    shutil.move(staging_file, target_file)
    print(f"[OK] Atomically published {len(v1_records)} V1 adaptation activities to {target_file}")
    return len(v1_records)

if __name__ == "__main__":
    convert_adaptation_records()
