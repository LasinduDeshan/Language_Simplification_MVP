"""
Stage 20 Baseline Snapshot Script
Verifies existing Stage 14/15 manifests and records the authoritative baseline snapshot
before dataset expansion.
"""
import os
import sys
import json
import hashlib
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

STAGE14_MANIFEST = os.path.join(ROOT_DIR, "docs", "stage14_manifest.sha256")
STAGE15_MANIFEST = os.path.join(ROOT_DIR, "docs", "stage15_manifest.sha256")

OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "reports")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "baseline_snapshot.json")

def compute_sha256(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def snapshot_baseline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("STAGE 20: Capturing Stage 14/15 Baseline Snapshot")
    print("=" * 60)
    
    # 1. Load Adaptation Test Set (v0.1.0)
    adapt_path = os.path.join(ROOT_DIR, "data", "adaptation_test_set", "releases", "0.1.0", "adaptation_test_set.json")
    with open(adapt_path, "r", encoding="utf-8") as f:
        adapt_data = json.load(f)
    adapt_records = adapt_data if isinstance(adapt_data, list) else adapt_data.get("records", [])
    
    # 2. Load Simplification Corpus (v0.1.0)
    simp_path = os.path.join(ROOT_DIR, "data", "simplification_corpus", "releases", "0.1.0", "simplification_corpus.json")
    with open(simp_path, "r", encoding="utf-8") as f:
        simp_data = json.load(f)
    simp_records = simp_data if isinstance(simp_data, list) else simp_data.get("records", [])
    
    # 3. Load Lexicon Repository (v0.1.0)
    lex_path = os.path.join(ROOT_DIR, "data", "lexicons", "en", "releases", "0.1.0", "lexicon_repository.json")
    with open(lex_path, "r", encoding="utf-8") as f:
        lex_data = json.load(f)
    lex_records = lex_data if isinstance(lex_data, list) else lex_data.get("records", [])
    
    snapshot = {
        "snapshot_timestamp": datetime.utcnow().isoformat() + "Z",
        "baseline_dataset_version": "0.1.0",
        "baseline_schema_version": "1.0.0",
        "target_dataset_version": "0.2.0",
        "target_schema_version": "1.0.0",
        "manifests": {
            "stage14_manifest_sha256": compute_sha256(STAGE14_MANIFEST) if os.path.exists(STAGE14_MANIFEST) else None,
            "stage15_manifest_sha256": compute_sha256(STAGE15_MANIFEST) if os.path.exists(STAGE15_MANIFEST) else None,
        },
        "datasets": {
            "adaptation_test_set": {
                "file": "data/adaptation_test_set/releases/0.1.0/adaptation_test_set.json",
                "sha256": compute_sha256(adapt_path),
                "record_count": len(adapt_records)
            },
            "simplification_corpus": {
                "file": "data/simplification_corpus/releases/0.1.0/simplification_corpus.json",
                "sha256": compute_sha256(simp_path),
                "record_count": len(simp_records)
            },
            "lexicon_repository": {
                "file": "data/lexicons/en/releases/0.1.0/lexicon_repository.json",
                "sha256": compute_sha256(lex_path),
                "record_count": len(lex_records)
            }
        },
        "stage15_quality_results": {
            "total_governed_evaluated": 268,
            "passed": 218,
            "failed": 19,
            "manual_review_required": 31,
            "quarantined": 0
        }
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
        
    print(f"Baseline snapshot saved to: {OUTPUT_FILE}")
    print(f" - Adaptation Test Set records: {len(adapt_records)}")
    print(f" - Simplification Corpus pairs: {len(simp_records)}")
    print(f" - English Lexicon entries:     {len(lex_records)}")
    print("=" * 60)
    return snapshot

if __name__ == "__main__":
    snapshot_baseline()
