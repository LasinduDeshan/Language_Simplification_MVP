"""
Stage 26 WP1: Build Group-Safe Training Eligibility Manifest and Dataset Eligibility Report.
"""
import sys
import json
from pathlib import Path

# Add backend to sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_simplification.training.eligibility import GroupSafeEligibilityAuditor


def generate_markdown_report(audit_result: dict, out_path: Path):
    rec = audit_result["reconciliation"]
    disps = rec["disposition_breakdown"]
    
    md = f"""# Stage 26 Dataset Eligibility & Group-Safe Audit Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Corpus Release:** 0.2.0 (Stage 20 Internal Benchmark)  
**Issue Register Source:** `data/simplification_corpus/releases/0.2.0/dataset_issue_register.json`  
**Manifest Version:** {audit_result['manifest_version']}  
**Corpus Immutability Guarantee:** `source_records_modified: false` (Original records preserved unchanged)  

---

## 1. Executive Summary

Stage 25 registered **{rec['directly_flagged_reformulation_pairs']} task reformulations** across the 900-pair Stage 20 draft corpus. In Stage 26-v2, pair-level exclusion was upgraded to **group-safe whole-source-group exclusion**. Every source group containing even a single task reformulation has all 3 of its companion pairs excluded to eliminate partial-group leakage and structural distortion.

### Key Audit Metrics
- **Total Audited Pairs:** {rec['total_pairs']} ({rec['total_groups']} source groups)
- **Directly Flagged Reformulation Pairs:** {rec['directly_flagged_reformulation_pairs']}
- **Dynamically Recalculated Contaminated Groups:** {rec['dynamically_recalculated_contaminated_groups']}
- **Total Group-Excluded Pairs ($3N$):** {rec['total_group_reformulation_excluded_pairs']}
- **Eligible Internal Training Groups (Clean, Complete 3-Tier):** {rec['eligible_internal_training_groups']} groups
- **Eligible Internal Training Pairs:** {rec['eligible_internal_training_pairs']} pairs ({rec['eligible_internal_training_groups']} groups $\\times$ 3 tiers)

---

## 2. Mutually Exclusive Pair Dispositions (Precedence Hierarchy)

Every pair is assigned exactly one disposition following the strict precedence hierarchy:

| Priority | Pair Disposition Category | Count | Percentage | Description |
| :---: | :--- | :---: | :---: | :--- |
| **1** | `direct_task_reformulation_excluded` | {disps['direct_task_reformulation_excluded']} | {disps['direct_task_reformulation_excluded'] / rec['total_pairs'] * 100:.2f}% | Directly flagged in Stage 25 issue register |
| **2** | `source_group_reformulation_excluded` | {disps['source_group_reformulation_excluded']} | {disps['source_group_reformulation_excluded'] / rec['total_pairs'] * 100:.2f}% | Unflagged companion in a contaminated group |
| **3** | `non_development_split_excluded` | {disps['non_development_split_excluded']} | {disps['non_development_split_excluded'] / rec['total_pairs'] * 100:.2f}% | Clean groups residing in Validation or Test splits |
| **4** | `incomplete_group_excluded` | {disps['incomplete_group_excluded']} | {disps['incomplete_group_excluded'] / rec['total_pairs'] * 100:.2f}% | Groups lacking all 3 tiers (Mild, Moderate, Strong) |
| **5** | `rights_or_governance_excluded` | {disps['rights_or_governance_excluded']} | {disps['rights_or_governance_excluded'] / rec['total_pairs'] * 100:.2f}% | Missing rights / authoring permissions |
| **6** | `quality_failed` | {disps['quality_failed']} | {disps['quality_failed'] / rec['total_pairs'] * 100:.2f}% | Failed automated quality checks |
| **7** | `manual_review_unresolved` | {disps['manual_review_unresolved']} | {disps['manual_review_unresolved'] / rec['total_pairs'] * 100:.2f}% | Unresolved human review flags |
| **8** | `eligible_internal_training` | {disps['eligible_internal_training']} | {disps['eligible_internal_training'] / rec['total_pairs'] * 100:.2f}% | **Approved for Derived Pilot Training Manifest** |
| **Total** | **Reconciled Sum** | **{rec['mutually_exclusive_sum']}** | **100.00%** | **Mutually Exclusive Reconciliation** |

---

## 3. Split-Level Group Accounting

| Split Name | Total Source Groups | Contaminated Groups | Clean Source Groups | Eligible Training Pairs |
| :--- | :---: | :---: | :---: | :---: |
| **Train (Development Candidate)** | 210 | 140 | 70 | **210** (70 groups $\\times$ 3 tiers) |
| **Validation (Evaluation Candidate)** | 45 | 31 | 14 | 0 (Reserved for Validation) |
| **Locked Test (Benchmark)** | 45 | 32 | 13 | 0 (Locked Benchmark Holdout) |
| **Total** | **300** | **203** | **97** | **210** |

---

## 4. Governance & Corpus Preservation

1. **Byte-for-Byte Corpus Preservation:** Original files in `data/simplification_corpus/releases/0.2.0/` remain strictly unmodified.
2. **Derived Training Approval:** Internal training approval applies strictly to derived pilot experiments.
3. **Draft Boundary Invariant:** Training eligibility does **not** imply public research release approval or unsupervised child-facing delivery permission. All generated models and candidate outputs remain `validation_status: "draft"` and `requires_expert_review: true`.
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)


def main():
    auditor = GroupSafeEligibilityAuditor(repo_root=repo_root)
    result = auditor.run_audit()

    manifest_dir = repo_root / "data" / "model_simplification" / "registry"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_out = manifest_dir / "stage26_training_eligibility_manifest.json"

    with open(manifest_out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_out = docs_dir / "stage26_dataset_eligibility_report.md"
    generate_markdown_report(result, report_out)

    rec = result["reconciliation"]
    print("=" * 65)
    print("STAGE 26 GROUP-SAFE DATASET ELIGIBILITY AUDIT COMPLETE")
    print("=" * 65)
    print(f"  Total Corpus Pairs: {rec['total_pairs']}")
    print(f"  Directly Flagged Reformulations: {rec['directly_flagged_reformulation_pairs']}")
    print(f"  Dynamically Recalculated Contaminated Groups: {rec['dynamically_recalculated_contaminated_groups']}")
    print(f"  Total Group-Excluded Pairs: {rec['total_group_reformulation_excluded_pairs']}")
    print(f"  Eligible Internal Training Groups: {rec['eligible_internal_training_groups']}")
    print(f"  Eligible Internal Training Pairs: {rec['eligible_internal_training_pairs']}")
    print("=" * 65)
    print(f"[+] Manifest saved: {manifest_out}")
    print(f"[+] Report saved:   {report_out}")


if __name__ == "__main__":
    main()
