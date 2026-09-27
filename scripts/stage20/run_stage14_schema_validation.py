"""
Stage 20 Script: Run Stage 14 Schema Validation
Validates all 5 authoring batches using AuthoringValidator and produces validation reports.
"""
import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.authoring_validator import AuthoringValidator

def main():
    print("=" * 60)
    print("STAGE 20: Running Stage 14 Schema Validation across all Batches")
    print("=" * 60)
    
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    validator = AuthoringValidator()
    
    overall_passed = True
    total_submitted = 0
    total_valid = 0
    total_failed = 0
    total_review = 0

    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                batch_data = json.load(f)
                
            res = validator.validate_batch(batch_data)
            total_submitted += res["total_submitted"]
            total_valid += res["total_valid"]
            total_failed += res["failed_count"]
            total_review += res["review_count"]
            
            print(f"Batch {res['batch_id']}:")
            print(f"  - Submitted: {res['total_submitted']}, Valid: {res['total_valid']}, Failed: {res['failed_count']}, Review: {res['review_count']}")
            if not res["is_schema_valid"]:
                overall_passed = False
                for err in res["failed_records"]:
                    print(f"    [ERROR] {err}")

    print("=" * 60)
    print("STAGE 14 SCHEMA VALIDATION SUMMARY:")
    print(f"  - Total Submitted Records: {total_submitted}")
    print(f"  - Total Valid Records:     {total_valid}")
    print(f"  - Total Failed Records:    {total_failed}")
    print(f"  - Total Review Records:    {total_review}")
    print(f"  - Overall Schema Status:   {'PASSED' if overall_passed else 'FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()
