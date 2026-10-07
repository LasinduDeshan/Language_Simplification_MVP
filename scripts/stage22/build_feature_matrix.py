"""Step 3: Feature registry export, feature matrix construction, and OOD bounds fitting."""

import sys
import json
from pathlib import Path
import pandas as pd
import joblib

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.feature_registry import (
    FEATURE_DEFINITIONS,
    FEATURE_ALLOWLIST,
    export_feature_dictionary,
)
from app.complexity_analysis.feature_builder import FeatureBuilder
from app.complexity_analysis.ood_detector import OODDetector
from app.complexity_analysis.repositories.feature_repository import FeatureRepository


def main():
    feat_repo = FeatureRepository()
    df_feats = feat_repo.load_features_df()
    records = df_feats.to_dict(orient="records")

    # Filter to training records for scaler & OOD fitting
    train_records = [
        r for r in records
        if r.get("dataset_split") == "development_candidate_train"
        and r.get("processing_status") == "success"
    ]
    print(f"Total training split records for fitting: {len(train_records)}")

    # 1. Export feature dictionary & schemas
    registry_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/feature_registry")
    registry_dir.mkdir(parents=True, exist_ok=True)

    dict_csv = registry_dir / "stage22_feature_dictionary.csv"
    export_feature_dictionary(dict_csv)

    docs_dict_csv = Path("docs/stage22_feature_dictionary.csv")
    docs_dict_csv.parent.mkdir(parents=True, exist_ok=True)
    export_feature_dictionary(docs_dict_csv)

    allowlist_json = registry_dir / "feature_allowlist.json"
    with open(allowlist_json, "w", encoding="utf-8") as f:
        json.dump(sorted(list(FEATURE_ALLOWLIST)), f, indent=2)

    schema_json = registry_dir / "feature_schema.json"
    with open(schema_json, "w", encoding="utf-8") as f:
        json.dump(FEATURE_DEFINITIONS, f, indent=2)

    print(f"Exported feature registry with {len(FEATURE_DEFINITIONS)} governed features.")

    # 2. Fit FeatureBuilder scaler on train records
    builder = FeatureBuilder()
    builder.fit(train_records)
    print("Fitted StandardScaler on training continuous features.")

    # 3. Fit OODDetector on train records
    df_train = builder.build_feature_dataframe(train_records)
    ood_detector = OODDetector(lower_quantile=0.01, upper_quantile=0.99)
    ood_detector.fit(df_train)
    print(f"Fitted OODDetector on {len(ood_detector.feature_bounds)} continuous features with [Q0.01, Q0.99] bounds.")

    # 4. Save preprocessor artifacts
    models_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/models")
    models_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(builder, models_dir / "preprocessing_transformer.joblib")
    joblib.dump(ood_detector, models_dir / "ood_detector.joblib")
    print(f"Saved preprocessing_transformer.joblib and ood_detector.joblib to {models_dir}")


if __name__ == "__main__":
    main()
