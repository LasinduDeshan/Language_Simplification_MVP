"""
Generates data/schemas/registry.json manifest for schema registry.
"""
import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REGISTRY_FILE = os.path.join(BASE_DIR, "data", "schemas", "registry.json")

def generate_schema_registry():
    print(f"=== GENERATING SCHEMA REGISTRY AT {REGISTRY_FILE} ===")
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)

    registry = {
        "registry_version": "1.0.0",
        "schemas": {
            "adaptation_record": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/adaptation_record.schema.json"
            },
            "simplification_pair": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/simplification_pair.schema.json"
            },
            "interaction_record": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/interaction_record.schema.json"
            },
            "interaction_export": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/interaction_export.schema.json"
            },
            "lexicon_entry": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/lexicon_entry.schema.json"
            },
            "release_manifest": {
                "current": "1.0.0",
                "supported": ["1.0.0"],
                "schema_file": "1.0.0/release_manifest.schema.json"
            }
        }
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"[OK] Schema registry written to {REGISTRY_FILE}")
    return True

if __name__ == "__main__":
    generate_schema_registry()
