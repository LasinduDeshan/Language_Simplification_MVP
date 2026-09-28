"""Step 2: Tiered label governance audit and label sufficiency verification."""

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

        # Rule seeded audit
        is_rule_seeded = False
        if annotator_tier == "heuristic_rule":
            is_rule_seeded = True

        audit_rec = auditor.audit_record(
            text_instance_id=text_id,
            parent_record_id=parent_id,
            parent_record_type=parent_type,
            source_group_id=source_group_id,
            assigned_difficulty=assigned_diff,
            annotator_tier=annotator_tier,
            provenance_source=provenance,
            derived_from_rule_heuristic=is_rule_seeded,
        )

        audit_records.append(audit_rec.model_dump())
        tier_counts[audit_rec.label_status] += 1
        if assigned_diff:
            label_counts[assigned_diff] += 1

    df_audit = pd.DataFrame(audit_records)

    print("=" * 60)
    print("STAGE 22 LABEL GOVERNANCE & AUDIT REPORT")
    print("=" * 60)
    for status, count in sorted(tier_counts.items()):
        print(f"  {status:25s}: {count:5d}")

    print("\nAssigned Difficulty Distribution (Across Labeled Records):")
    for diff, count in sorted(label_counts.items()):
        print(f"  {diff:10s}: {count:5d}")

    # Check Label-Sufficiency Stop Condition on Training Candidates
    train_records = [
        r for r, aud in zip(records, audit_records)
        if r.get("dataset_split") == "development_candidate_train"
        and aud["label_status"] in ("expert_verified", "reviewer_consensus")
    ]
    # Inject audited label data
    for tr, aud in zip(train_records, audit_records):
        tr["label_status"] = aud["label_status"]
        tr["assigned_difficulty"] = aud["assigned_difficulty"]
        tr["source_group_id"] = aud["source_group_id"]

    is_suff, max_folds, group_counts, message = auditor.evaluate_label_sufficiency(train_records)
    print(f"\nLabel-Sufficiency Check: {'PASSED' if is_suff else 'FAILED'}")
    print(f"  {message}")
    print(f"  Max Valid Folds: {max_folds}")

    if not is_suff:
        print("\n[CRITICAL ERROR] Insufficient Tier 1 labels for training. Stage 22 must pause.")
        sys.exit(1)

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
