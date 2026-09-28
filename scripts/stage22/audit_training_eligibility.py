"""Step 1: Mutually exclusive training eligibility determination and parent/instance accounting."""

import sys
from pathlib import Path
import pandas as pd
from collections import Counter

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.repositories.feature_repository import FeatureRepository
from app.complexity_analysis.repositories.label_repository import LabelRepository
from app.complexity_analysis.eligibility import evaluate_record_eligibility


def main():
    feat_repo = FeatureRepository()
    label_repo = LabelRepository()
    label_repo.load_all_labels()

    df_feats = feat_repo.load_features_df()
    records = df_feats.to_dict(orient="records")

    eligibility_records = []
    disposition_counts = Counter()

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

        if assigned_diff and annotator_tier in ("expert", "reviewer_consensus"):
            lbl_status = "expert_verified" if annotator_tier == "expert" else "reviewer_consensus"
        elif assigned_diff and annotator_tier == "provisional_author":
            lbl_status = "provisional"
        elif assigned_diff and annotator_tier == "heuristic_rule":
            lbl_status = "rule_seeded"
        else:
            lbl_status = "missing"

        # Check Stage 21 manual review flag if present
        manual_review = r.get("manual_review_required", False)
        if isinstance(manual_review, str):
            manual_review = manual_review.lower() in ("true", "1", "yes")

        elig = evaluate_record_eligibility(
            record=r,
            label_status=lbl_status,  # type: ignore
            manual_review_required=manual_review,
        )

        eligibility_records.append(elig.model_dump())
        disposition_counts[elig.primary_disposition] += 1

    df_elig = pd.DataFrame(eligibility_records)
    total_instances = len(df_elig)

    print("=" * 60)
    print("STAGE 22 MUTUALLY EXCLUSIVE ELIGIBILITY DISPOSITION")
    print("=" * 60)
    for disp, count in sorted(disposition_counts.items()):
        pct = (count / total_instances) * 100.0
        print(f"  {disp:32s}: {count:5d} ({pct:5.2f}%)")

    print(f"\nTotal Text Instances Accounted For: {total_instances} / 3617 (100.0%)")
    assert total_instances == 3617, f"Expected 3617, got {total_instances}"

    # Export reports
    out_dir_reports = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/reports")
    out_dir_reports.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir_reports / "eligibility_accounting.csv"
    df_elig.to_csv(out_csv, index=False)

    docs_csv = Path("docs/stage22_training_eligibility.csv")
    docs_csv.parent.mkdir(parents=True, exist_ok=True)
    df_elig.to_csv(docs_csv, index=False)

    print(f"\nSaved eligibility accounting to {out_csv} and {docs_csv}")


if __name__ == "__main__":
    main()
