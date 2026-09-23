"""
Schema registry loader and version compatibility validator for Stage 14 datasets.
"""
import os
import json
from typing import Dict, Any, List
from app.datasets.common.versions import parse_semver, CURRENT_SCHEMA_VERSION

SCHEMA_REGISTRY_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "data", "schemas", "registry.json"
))

DEFAULT_REGISTRY = {
    "registry_version": "1.0.0",
    "schemas": {
        "adaptation_record": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        },
        "simplification_pair": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        },
        "interaction_record": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        },
        "interaction_export": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        },
        "lexicon_entry": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        },
        "release_manifest": {
            "current": "1.0.0",
            "supported": ["1.0.0"]
        }
    }
}

class SchemaRegistry:
    def __init__(self, registry_path: str = SCHEMA_REGISTRY_PATH):
        self.registry_path = registry_path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return DEFAULT_REGISTRY

    def get_supported_versions(self, schema_name: str) -> List[str]:
        schema_info = self._data.get("schemas", {}).get(schema_name)
        if not schema_info:
            return ["1.0.0"]
        return schema_info.get("supported", ["1.0.0"])

    def validate_schema_version(self, schema_name: str, version_str: str) -> bool:
        """
        Validates if version_str is supported for schema_name.
        Raises ValueError if unsupported major version.
        """
        supported = self.get_supported_versions(schema_name)
        if version_str in supported:
            return True

        req_major, _, _ = parse_semver(version_str)
        curr_major, _, _ = parse_semver(CURRENT_SCHEMA_VERSION)

        if req_major > curr_major:
            raise ValueError(
                f"Unsupported future major schema version {version_str} for '{schema_name}'. "
                f"Current reader supports: {supported}"
            )
        elif req_major < curr_major:
            raise ValueError(
                f"Deprecated major schema version {version_str} for '{schema_name}'. "
                f"Please run migration script to upgrade to {CURRENT_SCHEMA_VERSION}."
            )
        return False

schema_registry = SchemaRegistry()
