"""
Stage 20 Script: Detect Duplicates
Runs multi-strategy duplicate detection across all authoring batches and writes docs/stage20_duplicate_report.csv.
"""
import os
import sys
import json
import csv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.datasets.expansion.duplicate_detector import DuplicateDetector

def main():
    print("=" * 60)
    print("STAGE 20: Running Multi-Strategy Duplicate Detection")
    print("=" * 60)
    
    batch_dir = os.path.join(ROOT_DIR, "data", "dataset_expansion", "stage20", "authoring_batches")
    all_source_items = []
    
    for filename in sorted(os.listdir(batch_dir)):
        if filename.endswith(".json"):
            filepath = os.path.join(batch_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_source_items.extend(data.get("source_items", []))

    detector = DuplicateDetector(jaccard_threshold=0.85, levenshtein_threshold=0.90)
    res = detector.scan_records(all_source_items, text_key="original_text", id_key="source_item_id")
    
    output_path = os.path.join(ROOT_DIR, "docs", "stage20_duplicate_report.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["check_type", "record_id_1", "record_id_2", "similarity_metric", "similarity_score", "status"])
        
        for ex in res["exact_duplicates"]:
            writer.writerow(["exact_normalized", ex["record_id"], ex["duplicate_of_id"], "exact_match", "1.00", "rejected_duplicate"])
            
        for near in res["near_duplicate_clusters"]:
            writer.writerow(["near_duplicate", near["record_id_1"], near["record_id_2"], "jaccard_similarity", near["jaccard_similarity"], "manual_review_required"])
            
        if len(res["exact_duplicates"]) == 0 and len(res["near_duplicate_clusters"]) == 0:
            writer.writerow(["summary", "N/A", "N/A", "total_duplicates", "0", "PASSED_ZERO_DUPLICATES"])

    print(f"Duplicate scan complete across {res['total_evaluated']} source items:")
    print(f"  - Exact duplicates found: {res['exact_duplicate_count']}")
    print(f"  - Near duplicate clusters: {res['near_duplicate_cluster_count']}")
    print(f"Report written to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
