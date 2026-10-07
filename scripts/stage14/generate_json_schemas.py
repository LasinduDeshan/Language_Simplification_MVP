"""
Generates JSON Schema Draft 2020-12 documents directly from Stage 14 Pydantic models.
"""
import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.insert(0, BACKEND_DIR)

from app.datasets.common.metadata import SourceMetadata, RightsMetadata, GovernanceMetadata
from app.datasets.common.release_manifest import ReleaseManifestV1
from app.datasets.adaptation_test_set.schemas import AdaptationRecordV1
from app.datasets.simplification_corpus.schemas import SimplificationPairV1
from app.datasets.interaction_dataset.schemas import PrivateInteractionRecordV1
from app.datasets.interaction_dataset.export_schemas import DeidentifiedInteractionExportV1
from app.datasets.lexicons.schemas import LexiconEntryV1

SCHEMAS_V1_DIR = os.path.join(BASE_DIR, "data", "schemas", "1.0.0")

def generate_json_schemas():
    os.makedirs(SCHEMAS_V1_DIR, exist_ok=True)
    print(f"=== GENERATING JSON SCHEMAS INTO {SCHEMAS_V1_DIR} ===")

    schemas = {
        "adaptation_record.schema.json": AdaptationRecordV1.model_json_schema(),
        "simplification_pair.schema.json": SimplificationPairV1.model_json_schema(),
        "interaction_record.schema.json": PrivateInteractionRecordV1.model_json_schema(),
        "interaction_export.schema.json": DeidentifiedInteractionExportV1.model_json_schema(),
        "lexicon_entry.schema.json": LexiconEntryV1.model_json_schema(),
        "release_manifest.schema.json": ReleaseManifestV1.model_json_schema(),
        "common_metadata.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "CommonMetadata",
            "type": "object",
            "properties": {
                "source": SourceMetadata.model_json_schema(),
                "rights": RightsMetadata.model_json_schema(),
                "governance": GovernanceMetadata.model_json_schema()
            },
            "required": ["source", "rights", "governance"]
        }
    }

    for filename, schema_dict in schemas.items():
        out_path = os.path.join(SCHEMAS_V1_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(schema_dict, f, indent=2)
        print(f"[OK] Generated {filename}")

    print("All JSON Schemas successfully generated from Pydantic models.")
    return True

if __name__ == "__main__":
    generate_json_schemas()
