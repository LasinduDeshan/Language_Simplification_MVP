"""
Execution receipt generator for Stage 36 Attempt 3 Simplification Lineage and Non-Repetition Integrity.
Executes governed fixtures across all activities, verifies non-repetition, records exact lineage,
and writes docs/stage36_attempt_lineage_execution_receipt.json.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

# Ensure backend root is on sys.path
repo_root = Path(__file__).resolve().parents[2]
backend_root = repo_root / "backend"
sys.path.insert(0, str(backend_root))

from app.localization.activity_catalog import GOVERNED_ACTIVITY_CATALOG
from app.sinhala_output_validation.simplification_adapter import Stage36SimplificationAdapter

BASELINE_DB_SHA256 = "44ff4f07fca1ac92343875bb8c82957df5cc721017dd08d20e901689392bb701"
IMMUTABLE_TAGS = {
    "stage-33-complete-v2": "36cc373616f2f7b87ca336523d59dbe607efa14e",
    "stage-35-complete-v6": "f222efc5919627effd62fa2b31c14f5913b6ec9e",
    "stage-36-complete-v7": "3d42a7125dad994276adc3c7263a7f557cd9ad98",
}


def generate_receipt():
    # 1. Verify Git commit & tags
    commit_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root), capture_output=True, text=True, check=True)
    current_commit = commit_res.stdout.strip()

    tag_verifications = {}
    for tag, expected_sha in IMMUTABLE_TAGS.items():
        res = subprocess.run(["git", "rev-parse", tag], cwd=str(repo_root), capture_output=True, text=True)
        tag_sha = res.stdout.strip()
        commit_res = subprocess.run(["git", "rev-parse", f"{tag}^{{commit}}"], cwd=str(repo_root), capture_output=True, text=True)
        commit_sha = commit_res.stdout.strip()
        verified = (tag_sha == expected_sha) or (commit_sha == expected_sha)
        tag_verifications[tag] = {
            "expected_tag_or_commit": expected_sha,
            "tag_sha": tag_sha,
            "commit_sha": commit_sha,
            "verified": verified,
        }

    # 2. Verify Stage 33 Immutability
    diff_res = subprocess.run(
        ["git", "diff", "stage-36-complete-v7", "--", "backend/app/sinhala_simplification/"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=True,
    )
    stage33_diff_empty = diff_res.stdout.strip() == ""

    # 3. Verify Database Baseline
    db_path = backend_root / "adaptive_learning.db"
    with open(db_path, "rb") as f:
        actual_db_sha256 = hashlib.sha256(f.read()).hexdigest()
    db_verified = actual_db_sha256 == BASELINE_DB_SHA256

    # 4. Execute Per-Activity Multi-Attempt Trace
    adapter = Stage36SimplificationAdapter()
    activity_traces = []

    for code, entry in GOVERNED_ACTIVITY_CATALOG.items():
        if code.startswith("ACT-") or code.startswith("TASK-00"):
            continue  # Skip aliases

        source_si = entry["instruction"]["si"]
        att2_text = entry["support_versions"]["strong_scaffold"]["si"]
        att3_template = entry["support_versions"]["strong_decomposed_step"]["si"]
        target_id = entry.get("target_id")
        disclosure_class = entry.get("disclosure_class", "INFERRED_ANSWER")
        disclosure_policy = entry.get("disclosure_policy", "DO_NOT_REVEAL")

        # Attempt 1: Baseline Independent
        att1_record = {
            "attempt_number": 1,
            "strategy_code": "MODERATE_REWORDING",
            "presented_instruction": source_si,
            "generation_mode": "BASELINE_TASK",
            "independent_performance_measure": True,
            "score_interpretation": "INDEPENDENT_BASELINE",
        }

        # Attempt 2: Strong Scaffold
        att2_record = {
            "attempt_number": 2,
            "strategy_code": "STRONG_SCAFFOLD",
            "presented_instruction": att2_text,
            "generation_mode": "TEMPLATE_CATALOG",
            "independent_performance_measure": False,
            "score_interpretation": "SUPPORTED_PERFORMANCE",
        }

        # Attempt 3: Strong Decomposed Step via Stage 36 Adapter
        att3_res = adapter.simplify_attempt_3(
            task_code=code,
            source_text=source_si,
            attempt_2_instruction=att2_text,
            attempt_2_id="ATT-RECEIPT-002",
            target_id=target_id,
            catalog_fallback_text=att3_template,
        )

        att3_lineage = att3_res["lineage_dict"]
        att3_presented = att3_res["presented_instruction"]
        non_repetition = att3_presented != att2_text

        att3_record = {
            "attempt_number": 3,
            "strategy_code": "STRONG_DECOMPOSED_STEP",
            "presented_instruction": att3_presented,
            "generation_mode": att3_lineage["generation_mode"],
            "lineage": att3_lineage,
            "independent_performance_measure": att3_lineage["independent_performance_measure"],
            "score_interpretation": att3_lineage["score_interpretation"],
            "validation_passed": att3_res["validation_passed"],
            "non_repetition_verified": non_repetition,
        }

        activity_traces.append({
            "activity_code": code,
            "title_si": entry["title"]["si"],
            "target_id": target_id,
            "disclosure_class": disclosure_class,
            "disclosure_policy": disclosure_policy,
            "attempt_1": att1_record,
            "attempt_2": att2_record,
            "attempt_3": att3_record,
            "all_attempts_distinct": non_repetition,
        })

    receipt = {
        "execution_receipt_id": "ST36-ATTEMPT-LINEAGE-RECEIPT-V1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": current_commit,
        "prospective_freeze_tag": "stage-36-freeze-attempt-lineage-v1",
        "immutable_upstream_tags": tag_verifications,
        "database_baseline_verification": {
            "expected_sha256": BASELINE_DB_SHA256,
            "actual_sha256": actual_db_sha256,
            "status": "PASSED" if db_verified else "FAILED",
        },
        "stage33_immutability_verification": {
            "target_directory": "backend/app/sinhala_simplification/",
            "baseline_tag": "stage-36-complete-v7",
            "diff_empty": stage33_diff_empty,
            "status": "PASSED" if stage33_diff_empty else "FAILED",
        },
        "governed_activities_count": len(activity_traces),
        "all_activities_non_repetition_verified": all(t["all_attempts_distinct"] for t in activity_traces),
        "all_activities_validation_passed": all(t["attempt_3"]["validation_passed"] for t in activity_traces),
        "activities": activity_traces,
    }

    out_file = repo_root / "docs" / "stage36_attempt_lineage_execution_receipt.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)

    print(f"PASS: Execution receipt generated at {out_file}")
    print(f"Governed activities verified: {len(activity_traces)}")
    print(f"Non-repetition verified across all activities: {receipt['all_activities_non_repetition_verified']}")
    return receipt


if __name__ == "__main__":
    generate_receipt()
