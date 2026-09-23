import os
import json
import pytest
from app.datasets.adaptation_test_set.schemas import AdaptationRecordV1
from app.datasets.simplification_corpus.schemas import SimplificationPairV1
from app.datasets.interaction_dataset.schemas import PrivateInteractionRecordV1
from app.datasets.interaction_dataset.export_schemas import DeidentifiedInteractionExportV1
from app.datasets.lexicons.schemas import LexiconEntryV1
from app.datasets.common.release_manifest import ReleaseManifestV1

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SCHEMAS_V1_DIR = os.path.join(BASE_DIR, "data", "schemas", "1.0.0")

def test_committed_json_schemas_match_pydantic_models():
    model_map = {
        "adaptation_record.schema.json": AdaptationRecordV1.model_json_schema(),
        "simplification_pair.schema.json": SimplificationPairV1.model_json_schema(),
        "interaction_record.schema.json": PrivateInteractionRecordV1.model_json_schema(),
        "interaction_export.schema.json": DeidentifiedInteractionExportV1.model_json_schema(),
        "lexicon_entry.schema.json": LexiconEntryV1.model_json_schema(),
        "release_manifest.schema.json": ReleaseManifestV1.model_json_schema()
    }

    for filename, expected_schema in model_map.items():
        disk_path = os.path.join(SCHEMAS_V1_DIR, filename)
        assert os.path.exists(disk_path), f"Missing JSON Schema file on disk: {disk_path}"
        with open(disk_path, "r", encoding="utf-8") as f:
            disk_schema = json.load(f)
        assert disk_schema == expected_schema, f"Parity mismatch in {filename}"
