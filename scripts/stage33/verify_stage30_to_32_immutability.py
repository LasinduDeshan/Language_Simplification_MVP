"""
Stage 33 — Stage 30-32 Immutability Verifier
Verifies that no Stage 30, Stage 31, or Stage 32 governed data, code, or documentation
artifacts have been modified in place relative to the immutable start tag stage-33-start.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
START_TAG = "stage-33-start"

PROTECTED_PATHS = [
    "data/sinhala_external",
    "data/sinhala_lexicon",
    "docs/stage30_preprocessing_specification.md",
    "docs/stage31_accounting_summary.md",
    "docs/stage31_acquisition_and_provenance_report.md",
    "docs/stage31_candidate_source_register.csv",
    "docs/stage31_completion_record.md",
    "docs/stage31_deduplication_and_contamination_report.md",
    "docs/stage31_governance_report.md",
    "docs/stage31_implementation_plan.md",
    "docs/stage31_licence_and_rights_report.md",
    "docs/stage31_manifest.sha256",
    "docs/stage31_pilot_corpus_report.md",
    "docs/stage31_preprocessing_integration_report.md",
    "docs/stage31_quality_and_exclusion_report.md",
    "docs/stage31_reproducibility_record.json",
    "docs/stage32_accounting_summary.md",
    "docs/stage32_completion_record.md",
    "docs/stage32_corpus_and_frequency_protocol.md",
    "docs/stage32_error_analysis.md",
    "docs/stage32_expert_review_readiness.md",
    "docs/stage32_implementation_plan.md",
    "docs/stage32_lexicon_evaluation_report.md",
    "docs/stage32_lexicon_governance_and_schema.md",
    "docs/stage32_manifest.sha256",
    "docs/stage32_morphology_and_surface_form_policy.md",
    "docs/stage32_provisional_banding_protocol.md",
    "docs/stage32_reproducibility_record.json",
    "docs/stage32_rights_and_export_report.md",
    "backend/app/datasets/sinhala_corpus",
    "backend/app/datasets/sinhala_lexicon",
    "backend/tests/sinhala_corpus",
    "backend/tests/sinhala_lexicon",
]


def verify_immutability():
    print("=== Stage 33 — Verifying Stage 30 to Stage 32 Immutability ===")
    cmd = ["git", "diff", "--name-status", f"{START_TAG}^{{commit}}", "HEAD", "--"] + PROTECTED_PATHS
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: git diff returned non-zero exit code {res.returncode}:\n{res.stderr}")
        sys.exit(1)

    diff_lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    if diff_lines:
        print(f"FAILED: Found {len(diff_lines)} modified Stage 30-32 files relative to {START_TAG}:")
        for line in diff_lines:
            print(f"  {line}")
        sys.exit(1)

    # Check working tree unstaged/staged diffs as well
    cmd_wt = ["git", "status", "--porcelain", "--"] + PROTECTED_PATHS
    res_wt = subprocess.run(cmd_wt, cwd=PROJECT_ROOT, capture_output=True, text=True)
    wt_lines = [line.strip() for line in res_wt.stdout.splitlines() if line.strip()]
    if wt_lines:
        print(f"FAILED: Found {len(wt_lines)} uncommitted working tree changes in Stage 30-32 paths:")
        for line in wt_lines:
            print(f"  {line}")
        sys.exit(1)

    print(f"PASSED: All {len(PROTECTED_PATHS)} Stage 30-32 paths are strictly immutable (0 differences).")


if __name__ == "__main__":
    verify_immutability()
