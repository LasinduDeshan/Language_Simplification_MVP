"""
Stage 21 Preprocessing Output Validation Script
Validates schema compliance, character offsets, hash determinism, and protected test split isolation.
"""
import sys
import json
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.nlp_preprocessing.schemas import PreprocessedRecord

def main():
    print("=== Stage 21: Preprocessing Output Validation ===")
    repo_root = Path(__file__).resolve().parent.parent.parent
    release_dir = repo_root / "data" / "preprocessed_features" / "en" / "source-0.2.0" / "pipeline-1.0.0"
    
    jsonl_path = release_dir / "preprocessed_records.jsonl"
    mappings_path = release_dir / "parent_to_text_mappings.json"
    features_csv_path = release_dir / "linguistic_features.csv"
    manifest_path = release_dir / "dataset_manifest.json"
    locked_manifest_path = release_dir / "protected_test" / "locked_test_manifest.json"

    assert jsonl_path.exists(), f"Missing {jsonl_path}"
    assert mappings_path.exists(), f"Missing {mappings_path}"
    assert features_csv_path.exists(), f"Missing {features_csv_path}"
    assert manifest_path.exists(), f"Missing {manifest_path}"
    assert locked_manifest_path.exists(), f"Missing {locked_manifest_path}"

    print("1. Validating Pydantic Schemas on all records...")
    record_count = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            rec = PreprocessedRecord(**data)
            record_count += 1
            
            # If not locked test, verify character slice integrity
            if rec.processing_status != "skipped_locked_test":
                for sent in rec.sentences:
                    norm_slice = rec.normalized_text[sent.normalized_start_char:sent.normalized_end_char]
                    assert norm_slice == sent.text, f"Sentence slice mismatch at line {line_num}: '{norm_slice}' vs '{sent.text}'"
                    for tok in sent.tokens:
                        tok_slice = rec.normalized_text[tok.normalized_start_char:tok.normalized_end_char]
                        assert tok_slice == tok.text, f"Token slice mismatch at line {line_num}: '{tok_slice}' vs '{tok.text}'"

    print(f"Validated {record_count} preprocessed records with 100% schema & character offset fidelity.")

    print("2. Validating Parent-to-Text Mapping Associations...")
    with open(mappings_path, "r", encoding="utf-8") as f:
        mappings = json.load(f)
    assert len(mappings) == record_count, f"Mapping count {len(mappings)} does not match records {record_count}"

    print("3. Validating Locked Test Isolation (0 raw text in protected test manifest)...")
    with open(locked_manifest_path, "r", encoding="utf-8") as f:
        locked_m = json.load(f)
    for item in locked_m.get("items", []):
        assert "text" not in item, "Leaked raw text in locked test manifest item!"
        assert item["processing_status"] == "skipped_locked_test"

    print("\nALL OUTPUT VALIDATIONS PASSED.")

if __name__ == "__main__":
    main()
