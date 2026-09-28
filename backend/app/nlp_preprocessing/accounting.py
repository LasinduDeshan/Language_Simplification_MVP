"""
Stage 21 Preprocessing Accounting & Zero-Loss Reconciliation Module
"""
import os
import csv
from typing import List, Dict, Any

class PreprocessingAccounting:
    def __init__(self):
        pass

    def reconcile(
        self,
        raw_text_instances: List[Any],
        processed_records: List[Any],
        parent_mappings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        raw_count = len(raw_text_instances)
        output_count = len(processed_records)
        
        # Unique normalized texts
        seen_texts = set()
        for inst in raw_text_instances:
            seen_texts.add(inst.text.strip())
        unique_text_count = len(seen_texts)
        duplicate_text_count = max(0, raw_count - unique_text_count)
        
        # Dispositions
        success_count = sum(1 for r in processed_records if r.processing_status == "success")
        fallback_count = sum(1 for r in processed_records if r.processing_status == "fallback_success")
        review_count = sum(1 for r in processed_records if r.processing_status == "manual_review_required")
        failed_count = sum(1 for r in processed_records if r.processing_status == "failed")
        skipped_test_count = sum(1 for r in processed_records if r.processing_status == "skipped_locked_test")
        
        accounted = success_count + fallback_count + review_count + failed_count + skipped_test_count
        unaccounted = raw_count - accounted

        return {
            "raw_text_instance_count": raw_count,
            "unique_normalized_text_count": unique_text_count,
            "duplicate_text_instance_count": duplicate_text_count,
            "parent_text_mapping_count": len(parent_mappings),
            "success_count": success_count,
            "fallback_success_count": fallback_count,
            "manual_review_count": review_count,
            "failed_count": failed_count,
            "skipped_locked_test_count": skipped_test_count,
            "total_accounted": accounted,
            "unaccounted_records": unaccounted,
            "is_zero_loss": (unaccounted == 0)
        }

    def generate_csv_report(self, summary: Dict[str, Any], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["metric_name", "count", "percentage", "reconciliation_status"])
            
            raw_cnt = max(1, summary["raw_text_instance_count"])
            writer.writerow(["Raw Text Instances Extracted", summary["raw_text_instance_count"], "100.0%", "EXTRACTED"])
            writer.writerow(["Unique Normalized Texts Processed", summary["unique_normalized_text_count"], f"{summary['unique_normalized_text_count']/raw_cnt*100:.1f}%", "PROCESSED"])
            writer.writerow(["Duplicate Text Instances (Cached/Mapped)", summary["duplicate_text_instance_count"], f"{summary['duplicate_text_instance_count']/raw_cnt*100:.1f}%", "DEDUPLICATED"])
            writer.writerow(["Parent-to-Text Associations Preserved", summary["parent_text_mapping_count"], "N/A", "PRESERVED_MANY_TO_MANY"])
            writer.writerow(["Primary Pipeline Success", summary["success_count"], f"{summary['success_count']/raw_cnt*100:.1f}%", "RECONCILED"])
            writer.writerow(["Fallback Pipeline Success", summary["fallback_success_count"], f"{summary['fallback_success_count']/raw_cnt*100:.1f}%", "RECONCILED"])
            writer.writerow(["Manual Review Required", summary["manual_review_count"], f"{summary['manual_review_count']/raw_cnt*100:.1f}%", "RECONCILED"])
            writer.writerow(["Processing Failed", summary["failed_count"], f"{summary['failed_count']/raw_cnt*100:.1f}%", "RECONCILED"])
            writer.writerow(["Skipped Locked Test Records", summary["skipped_locked_test_count"], f"{summary['skipped_locked_test_count']/raw_cnt*100:.1f}%", "GUARDED_ISOLATION"])
            writer.writerow(["Unaccounted Records", summary["unaccounted_records"], "0.0%", "ZERO_LOSS_VERIFIED" if summary["is_zero_loss"] else "ERROR_LEAK"])
