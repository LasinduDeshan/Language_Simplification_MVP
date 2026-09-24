"""Quality validation report generator separating public aggregates from private diagnostic logs."""
import os
import json
import csv
import datetime
from typing import List, Dict, Any
from app.datasets.quality.models import ValidationRun, RecordQualitySummary, QualityRuleResult, ManualReviewQueueEntry
from app.datasets.common.paths import PROJECT_ROOT

PUBLIC_REPORT_DIR = os.path.join(PROJECT_ROOT, "data", "quality_reports", "stage15", "public")
PRIVATE_REPORT_DIR = os.path.join(PROJECT_ROOT, "data", "quality_reports", "stage15", "private")


class QualityReportGenerator:
    """Generates structured public CSV/JSON reports and git-ignored private failure logs."""

    @classmethod
    def generate_reports(
        cls,
        run: ValidationRun,
        summaries: List[RecordQualitySummary],
        results: List[QualityRuleResult],
        review_entries: List[ManualReviewQueueEntry],
        base_dir: str = ""
    ) -> Dict[str, str]:
        """Generates all public and private Stage 15 reports."""
        pub_dir = os.path.join(base_dir, "data", "quality_reports", "stage15", "public") if base_dir else PUBLIC_REPORT_DIR
        priv_dir = os.path.join(base_dir, "data", "quality_reports", "stage15", "private") if base_dir else PRIVATE_REPORT_DIR

        os.makedirs(pub_dir, exist_ok=True)
        os.makedirs(priv_dir, exist_ok=True)

        generated_paths = {}

        # 1. Public JSON Report (Aggregated metrics, zero PII or raw texts)
        pub_json_path = os.path.join(pub_dir, "stage15_quality_report.json")
        pub_data = {
            "run_id": run.run_id,
            "dataset_layer": run.dataset_layer,
            "dataset_version": run.dataset_version,
            "quality_rule_set_version": run.quality_rule_set_version,
            "status": run.status,
            "total_records": run.total_records,
            "accounting": {
                "passed_count": run.passed_count,
                "failed_count": run.failed_count,
                "review_required_count": run.review_required_count,
                "quarantined_count": run.quarantined_count,
                "unaccounted_count": run.total_records - (run.passed_count + run.failed_count + run.review_required_count + run.quarantined_count)
            },
            "created_at": run.created_at.isoformat() if run.created_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None
        }
        with open(pub_json_path, "w", encoding="utf-8") as f:
            json.dump(pub_data, f, indent=2)
        generated_paths["public_json"] = pub_json_path

        # 2. Public CSV Summary (Per-record scores and status, no raw texts)
        pub_csv_path = os.path.join(pub_dir, "stage15_quality_summary.csv")
        with open(pub_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "summary_id", "record_id", "dataset_layer", "quality_status",
                "overall_quality_score", "rules_executed", "rules_passed",
                "warnings_count", "errors_count", "critical_count",
                "requires_expert_review", "research_eligible", "approved_for_child_delivery"
            ])
            for s in summaries:
                writer.writerow([
                    s.summary_id, s.record_id, s.dataset_layer, s.quality_status,
                    s.overall_quality_score, s.rules_executed, s.rules_passed,
                    s.warnings_count, s.errors_count, s.critical_count,
                    s.requires_expert_review, s.research_eligible, s.approved_for_child_delivery
                ])
        generated_paths["public_csv"] = pub_csv_path

        # 3. Private Review Queue CSV (Untracked)
        priv_queue_path = os.path.join(priv_dir, "stage15_manual_review_queue.csv")
        with open(priv_queue_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "entry_id", "record_id", "dataset_layer", "priority",
                "triggering_rule_ids", "summary", "review_status", "assigned_reviewer_id"
            ])
            for q in review_entries:
                writer.writerow([
                    q.entry_id, q.record_id, q.dataset_layer, q.priority,
                    ",".join(q.triggering_rule_ids if isinstance(q.triggering_rule_ids, list) else []),
                    q.summary, q.review_status, q.assigned_reviewer_id or ""
                ])
        generated_paths["private_queue_csv"] = priv_queue_path

        # 4. Private Validation Failures CSV (Untracked)
        priv_failures_path = os.path.join(priv_dir, "stage15_validation_failures.csv")
        with open(priv_failures_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "result_id", "record_id", "dataset_layer", "rule_id",
                "validator_name", "severity", "message", "recommended_action"
            ])
            for r in results:
                if not r.passed:
                    writer.writerow([
                        r.result_id, r.record_id, r.dataset_layer, r.rule_id,
                        r.validator_name, r.severity, r.message, r.recommended_action or ""
                    ])
        generated_paths["private_failures_csv"] = priv_failures_path

        return generated_paths
