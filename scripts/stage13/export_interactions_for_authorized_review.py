import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.database.db import SessionLocal
from app.datasets.interaction_dataset.repository import InteractionRepository
from app.datasets.common.draft_models import MigrationMappingRecord, MigrationDisposition
from app.datasets.common.paths import INTERACTION_ID_MAPPINGS_DIR

def export_private_interactions():
    print("=== EXPORTING PRIVATE INTERACTIONS (DATABASE AS TRUTH) ===")
    
    db = SessionLocal()
    try:
        repo = InteractionRepository()
        snapshot_path = repo.export_private_snapshot(db=db, output_filename="private_interactions_snapshot.json")
        print(f"Exported audited private interactions snapshot to: {snapshot_path}")

        # Generate interaction ID mappings
        with open(snapshot_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        os.makedirs(INTERACTION_ID_MAPPINGS_DIR, exist_ok=True)
        mappings = []
        for r in records:
            mappings.append(MigrationMappingRecord(
                source_path="db_table:attempts",
                source_id=r.get("session_id", ""),
                target_layer="interaction_dataset/private",
                target_id=r.get("interaction_id", ""),
                disposition=MigrationDisposition.MIGRATED,
                notes=f"Learner: {r.get('learner_id')}, Domain: {r.get('updated_domain')}"
            ).model_dump(mode="json"))

        mapping_file = os.path.join(INTERACTION_ID_MAPPINGS_DIR, "interaction_id_mappings.json")
        with open(mapping_file, "w", encoding="utf-8") as f:
            json.dump(mappings, f, indent=2)

        print(f"Generated {len(mappings)} interaction ID mappings.")
        return len(records)
    finally:
        db.close()

if __name__ == "__main__":
    export_private_interactions()
