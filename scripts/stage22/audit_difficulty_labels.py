"""Step 2: Tiered label governance audit, provenance tracking, and pilot sufficiency verification."""

import sys
from pathlib import Path
import pandas as pd
from collections import Counter

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.repositories.feature_repository import FeatureRepository
from app.complexity_analysis.repositories.label_repository import LabelRepository
from app.complexity_analysis.label_auditor import LabelAuditor


def main():
    feat_repo = FeatureRepository()
    label_repo = LabelRepository()
    label_repo.load_all_labels()
    auditor = LabelAuditor(min_folds_groups=3)

    df_feats = feat_repo.load_features_df()
    records = df_feats.to_dict(orient="records")

    audit_records = []
    tier_counts = Counter()
    label_counts = Counter()

    for r in records:
        text_id = r["text_instance_id"]
        parent_id = r.get("parent_record_id", "")
        parent_type = r.get("parent_record_type", "")
        text_role = r.get("text_role", "")

        label_info = label_repo.get_label_for_instance(
            text_instance_id=text_id,
            parent_record_id=parent_id,
            parent_record_type=parent_type,
            text_role=text_role,
        )

        assigned_diff = label_info.get("assigned_difficulty")
        annotator_tier = label_info.get("annotator_tier", "none")
        provenance = label_info.get("provenance_source", "unassigned")
        source_group_id = label_info.get("source_group_id") or parent_id

        is_rule_seeded = annotator_tier == "heuristic_rule"

        audit_rec = auditor.audit_record(
            text_instance_id=text_id,
            parent_record_id=parent_id,
            parent_record_type=parent_type,
            source_group_id=source_group_id,
            assigned_difficulty=assigned_diff,
            annotator_tier=annotator_tier,
            provenance_source=provenance,
            derived_from_rule_heuristic=is_rule_seeded,
            reviewer_reference=label_info.get("reviewer_reference", "None (Draft authoring item awaiting expert panel review)"),
            reviewer_role=label_info.get("reviewer_role", "provisional_author"),
            annotation_guideline_version=label_info.get("annotation_guideline_version", "v1.0.0-draft"),
            reviewed_at=label_info.get("reviewed_at"),
            agreement_status=label_info.get("agreement_status", "single_author_provisional"),
            adjudication_status=label_info.get("adjudication_status", "pending_expert_adjudication"),
        )

        audit_records.append(audit_rec.model_dump())
        tier_counts[audit_rec.label_status] += 1
        if assigned_diff:
            label_counts[assigned_diff] += 1

    df_audit = pd.DataFrame(audit_records)

    print("=" * 60)
    print("STAGE 22 LABEL GOVERNANCE & PROVENANCE AUDIT REPORT")
    print("=" * 60)
    for status, count in sorted(tier_counts.items()):
        print(f"  {status:25s}: {count:5d}")

    print("\nAssigned Difficulty Distribution (Across Labeled Records):")
    for diff, count in sorted(label_counts.items()):
        print(f"  {diff:10s}: {count:5d}")

    # Check Label-Sufficiency on Provisional Training Candidates (Pilot Level)
    train_records = [
        r for r, aud in zip(records, audit_records)
        if r.get("dataset_split") == "development_candidate_train"
        and aud["assigned_difficulty"] is not None
        and not r.get("manual_review_required", False)
    ]
    for tr, aud in zip(train_records, audit_records):
        tr["label_status"] = aud["label_status"]
        tr["assigned_difficulty"] = aud["assigned_difficulty"]
        tr["source_group_id"] = aud["source_group_id"]

    is_suff, max_folds, group_counts, message = auditor.evaluate_label_sufficiency(train_records, tier_1_only=False)
    print(f"\nPilot Label-Sufficiency Check: {'PASSED' if is_suff else 'FAILED'}")
    print(f"  {message}")
    print(f"  Max Valid Folds: {max_folds}")

    # Export reports
    out_dir_reports = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/reports")
    out_dir_reports.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir_reports / "label_audit.csv"
    df_audit.to_csv(out_csv, index=False)

    docs_csv = Path("docs/stage22_label_audit.csv")
    df_audit.to_csv(docs_csv, index=False)
    print(f"\nSaved label audit to {out_csv} and {docs_csv}")


if __name__ == "__main__":
    main()
