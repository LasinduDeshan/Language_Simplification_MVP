"""
Converts Stage 13 Lexicon entries into V1 Pydantic models and atomically publishes release 0.1.0.
"""
import os
import sys
import json
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.lexicons.schemas import LexiconEntryV1
from app.datasets.common.enums import LanguageCode, SourceType, ValidationStatus, ResearchEligibilityStatus
from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata

SOURCE_FILE = os.path.join(BASE_DIR, "data", "lexicons", "en", "tiered_vocabulary_lexicon.json")
RELEASE_DIR = os.path.join(BASE_DIR, "data", "lexicons", "en", "releases", "0.1.0")

def convert_lexicon_entries():
    print(f"=== CONVERTING LEXICON ENTRIES TO V1 (RELEASE 0.1.0) ===")
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw_entries = json.load(f)

    v1_entries = []
    counter = 1
    for raw in raw_entries:
        entry_id = f"LEX-EN-{counter:06d}"
        counter += 1

        word = raw["word"].strip()
        simpler = []
        if "simple_alternative" in raw and raw["simple_alternative"]:
            simpler.append(raw["simple_alternative"].strip())
        elif "simpler_alternatives" in raw and raw["simpler_alternatives"]:
            simpler.extend(raw["simpler_alternatives"])

        diff_str = raw.get("difficulty", "medium")
        tier = 1 if diff_str == "easy" else (3 if diff_str == "hard" else 2)

        entry = LexiconEntryV1(
            entry_id=entry_id,
            schema_version="1.0.0",
            dataset_version="0.1.0",
            language=LanguageCode.EN,
            word=word,
            normalized_form=word.lower(),
            part_of_speech=raw.get("part_of_speech"),
            age_band=f"{raw.get('minimum_age', 4)}-8",
            difficulty_tier=tier,
            simpler_alternatives=simpler,
            child_friendly_definition=raw.get("simple_definition") or raw.get("child_friendly_definition"),
            example_sentence=raw.get("example_sentence"),
            source=SourceMetadata(
                source_type=SourceType.EXPERT_AUTHORED if raw.get("source") == "expert_reviewed_project_resource" else SourceType.TEAM_AUTHORED,
                source_name="Component 3 English MVP Tiered Lexicon",
                source_record_id=word,
                created_by_role="linguist"
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
        v1_entries.append(entry)

    # Validate all through Pydantic
    serialized = [e.model_dump(mode="json") for e in v1_entries]
    
    # Atomic staging
    os.makedirs(RELEASE_DIR, exist_ok=True)
    staging_file = os.path.join(RELEASE_DIR, ".staging_lexicon_repository.json")
    target_file = os.path.join(RELEASE_DIR, "lexicon_repository.json")

    with open(staging_file, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2)

    shutil.move(staging_file, target_file)
    print(f"[OK] Atomically published {len(v1_entries)} V1 lexicon entries to {target_file}")
    return len(v1_entries)

if __name__ == "__main__":
    convert_lexicon_entries()
