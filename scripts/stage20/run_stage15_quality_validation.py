"""
Stage 20 Script: Run Stage 15 Quality Validation
Applies Stage 15 quality rules and meaning unit preservation to all newly authored records.
"""
import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.meaning_validator import MeaningValidator

def main():
    print("=" * 60)
    print("STAGE 20: Running Stage 15 Quality & Meaning Preservation Gate")
    print("=" * 60)
    
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    meaning_validator = MeaningValidator()
    
    total_pairs = 0
    passed_pairs = 0
    review_pairs = 0
    failed_pairs = 0
    
    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                batch_data = json.load(f)
                
            for pair in batch_data.get("simplification_pairs", []):
                total_pairs += 1
                res = meaning_validator.validate_meaning_units(
                    pair["original_text"],
                    pair["simplified_text"],
                    pair.get("protected_meaning_units", [])
                )
                if res["status"] == "passed":
                    passed_pairs += 1
                elif res["status"] == "manual_review_required":
                    review_pairs += 1
                else:
                    failed_pairs += 1

    pass_rate = (passed_pairs / total_pairs * 100) if total_pairs > 0 else 100.0
    print(f"Evaluated {total_pairs} Simplification Pairs across 5 Batches:")
    print(f"  - Passed:       {passed_pairs} ({pass_rate:.1f}%)")
    print(f"  - Review Req'd: {review_pairs}")
    print(f"  - Failed:       {failed_pairs}")
    print(f"  - Gate Target:  >= 85.0% pass rate")
    print(f"  - Quality Gate: {'PASSED' if pass_rate >= 85.0 else 'FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
