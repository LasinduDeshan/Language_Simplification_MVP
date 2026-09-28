"""Step 4: Cross-validation, probability calibration, model comparison, and error analysis."""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Set
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
import joblib

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.repositories.feature_repository import FeatureRepository
from app.complexity_analysis.repositories.label_repository import LabelRepository
from app.complexity_analysis.feature_builder import FeatureBuilder
from app.complexity_analysis.leakage_guard import LeakageGuard
from app.complexity_analysis.label_auditor import LabelAuditor
from app.complexity_analysis.calibration import ProbabilityCalibrator
from app.complexity_analysis.evaluator import ModelEvaluator
from app.complexity_analysis.models import (
    MajorityBaselineClassifier,
    TransparentRuleClassifier,
    MultinomialLogisticClassifier,
    ConstrainedDecisionTreeClassifier,
    RandomForestComplexityClassifier,
    HistGradientBoostingComplexityClassifier,
)


LABEL_MAP = {"easy": 0, "medium": 1, "hard": 2}
INV_LABEL_MAP = {0: "easy", 1: "medium", 2: "hard"}


def prepare_dataset(feat_repo: FeatureRepository, label_repo: LabelRepository):
    df_feats = feat_repo.load_features_df()
    records = df_feats.to_dict(orient="records")

    train_candidates = []
    val_candidates = []

    for r in records:
        if r.get("processing_status") != "success":
            continue

        split = r.get("dataset_split")
        if split not in ("development_candidate_train", "development_candidate_validation"):
            continue

        label_info = label_repo.get_label_for_instance(
            text_instance_id=r["text_instance_id"],
            parent_record_id=r.get("parent_record_id", ""),
            parent_record_type=r.get("parent_record_type", ""),
            text_role=r.get("text_role", ""),
        )

        diff = label_info.get("assigned_difficulty")
        tier = label_info.get("annotator_tier")

        if diff in LABEL_MAP and tier in ("expert", "reviewer_consensus"):
            r_copy = dict(r)
            r_copy["assigned_difficulty"] = diff
            r_copy["difficulty_target"] = LABEL_MAP[diff]
            r_copy["source_group_id"] = label_info.get("source_group_id") or r.get("parent_record_id")
            r_copy["annotator_tier"] = tier
            r_copy["label_status"] = "expert_verified" if tier == "expert" else "reviewer_consensus"

            if split == "development_candidate_validation":
                val_candidates.append(r_copy)
            elif split == "development_candidate_train":
                train_candidates.append(r_copy)

    # Enforce strict group & hash isolation: eliminate any train instances sharing group or hash with val
    val_groups: Set[str] = {r["source_group_id"] for r in val_candidates}
    val_hashes: Set[str] = {r["text_hash"] for r in val_candidates if r.get("text_hash")}

    pure_train = [
        r for r in train_candidates
        if r["source_group_id"] not in val_groups and r.get("text_hash") not in val_hashes
    ]

    return pure_train, val_candidates


def main():
    feat_repo = FeatureRepository()
    label_repo = LabelRepository()
    label_repo.load_all_labels()

    train_records, val_records = prepare_dataset(feat_repo, label_repo)

    print(f"Loaded {len(train_records)} isolated Tier 1 train records and {len(val_records)} Tier 1 validation records.")

    # 1. Anti-Leakage Verification
    group_clean, group_overlap = LeakageGuard.check_group_leakage(train_records, val_records)
    hash_clean, hash_overlap = LeakageGuard.check_hash_leakage(train_records, val_records)
    locked_clean, locked_viols = LeakageGuard.check_locked_test_quarantine(train_records + val_records)

    print("Leakage Checks:")
    print(f"  Group Containment: {'PASSED' if group_clean else f'FAILED ({len(group_overlap)} overlaps)'}")
    print(f"  Hash Containment : {'PASSED' if hash_clean else f'FAILED ({len(hash_overlap)} overlaps)'}")
    print(f"  Locked Test Isolation: {'PASSED' if locked_clean else f'FAILED ({len(locked_viols)} violations)'}")

    assert group_clean, f"Group leakage detected: {group_overlap}"
    assert hash_clean, f"Hash leakage detected: {hash_overlap}"
    assert locked_clean, f"Locked test violations: {locked_viols}"

    # 2. Label Sufficiency Gate
    auditor = LabelAuditor(min_folds_groups=3)
    is_suff, max_folds, group_counts, msg = auditor.evaluate_label_sufficiency(train_records)
    print(f"\nLabel Sufficiency Check: {msg}")
    assert is_suff, f"Label sufficiency failed: {msg}"

    # 3. Fit Feature Builder on Train records
    feature_builder = FeatureBuilder()
    X_train = feature_builder.fit_transform(train_records)
    y_train = np.array([r["difficulty_target"] for r in train_records], dtype=int)
    groups_train = [r["source_group_id"] for r in train_records]

    X_val = feature_builder.transform(val_records)
    y_val = np.array([r["difficulty_target"] for r in val_records], dtype=int)

    # 4. Model Candidates Definition
    candidates = [
        MajorityBaselineClassifier(),
        TransparentRuleClassifier(),
        MultinomialLogisticClassifier(C=1.0, random_state=42),
        ConstrainedDecisionTreeClassifier(max_depth=4, min_samples_leaf=10, random_state=42),
        RandomForestComplexityClassifier(n_estimators=100, max_depth=6, min_samples_leaf=5, random_state=42),
        HistGradientBoostingComplexityClassifier(max_iter=100, max_leaf_nodes=31, min_samples_leaf=10, random_state=42),
    ]

    sgkf = StratifiedGroupKFold(n_splits=3)
    oof_predictions: Dict[str, np.ndarray] = {}
    fitted_models: Dict[str, Any] = {}
    comparison_rows = []

    print("\n" + "=" * 80)
    print("STAGE 22 MODEL TRAINING & CROSS-VALIDATION")
    print("=" * 80)

    for clf in candidates:
        m_id = clf.model_id
        m_name = clf.model_name
        print(f"\nTraining [{m_id}] {m_name}...")

        oof_prob = np.zeros((len(X_train), 3), dtype=np.float64)
        t0 = time.time()

        # OOF Cross Validation
        for train_idx, val_idx in sgkf.split(X_train, y_train, groups=groups_train):
            clf_fold = clf.__class__()
            clf_fold.fit(X_train[train_idx], y_train[train_idx])
            oof_prob[val_idx] = clf_fold.predict_proba(X_train[val_idx])

        fit_time = time.time() - t0
        oof_predictions[m_id] = oof_prob

        # Fit on full training split
        clf.fit(X_train, y_train)
        fitted_models[m_id] = clf

        # Evaluate on validation split
        t_lat0 = time.time()
        y_val_prob = clf.predict_proba(X_val)
        lat_ms = ((time.time() - t_lat0) / max(1, len(X_val))) * 1000.0
        y_val_pred = np.argmax(y_val_prob, axis=1)

        summary, cm = ModelEvaluator.evaluate(
            model_id=m_id,
            model_name=m_name,
            y_true=y_val,
            y_pred=y_val_pred,
            y_prob=y_val_prob,
            split_name="validation",
            fit_time_seconds=fit_time,
            latency_ms=lat_ms,
        )

        row = {
            "model_id": m_id,
            "model_name": m_name,
            "macro_f1": round(summary.macro_f1, 4),
            "weighted_f1": round(summary.weighted_f1, 4),
            "balanced_accuracy": round(summary.balanced_accuracy, 4),
            "accuracy": round(summary.accuracy, 4),
            "recall_easy": round(summary.per_class_recall["easy"], 4),
            "recall_medium": round(summary.per_class_recall["medium"], 4),
            "recall_hard": round(summary.per_class_recall["hard"], 4),
            "expected_calibration_error": round(summary.expected_calibration_error, 4),
            "hard_to_easy_error_rate": round(summary.hard_to_easy_error_rate, 4),
            "hard_to_easy_error_count": summary.hard_to_easy_error_count,
            "hard_to_easy_wilson_ci": f"[{summary.hard_to_easy_wilson_ci_lower:.4f}, {summary.hard_to_easy_wilson_ci_upper:.4f}]",
            "fit_time_seconds": round(fit_time, 3),
            "inference_latency_ms": round(lat_ms, 3),
        }
        comparison_rows.append(row)
        print(f"  Validation Macro-F1: {summary.macro_f1:.4f} | Balanced Acc: {summary.balanced_accuracy:.4f} | ECE: {summary.expected_calibration_error:.4f} | Hard->Easy: {summary.hard_to_easy_error_rate:.2%}")

    df_comp = pd.DataFrame(comparison_rows)
    print("\n" + "=" * 80)
    print("STAGE 22 MODEL COMPARISON BENCHMARK (VALIDATION SPLIT)")
    print("=" * 80)
    print(df_comp[["model_id", "model_name", "macro_f1", "balanced_accuracy", "expected_calibration_error", "hard_to_easy_error_rate"]].to_string(index=False))

    # Select Champion Model (Highest Macro-F1 / Balanced Accuracy)
    best_row = df_comp.sort_values(by=["macro_f1", "balanced_accuracy"], ascending=False).iloc[0]
    champion_id = best_row["model_id"]
    champion_model = fitted_models[champion_id]
    print(f"\nChampion Model Selected: [{champion_id}] {champion_model.model_name}")

    # Fit Probability Calibration on Champion's OOF Predictions
    calibrator = ProbabilityCalibrator(method="isotonic")
    calibrator.fit(oof_predictions[champion_id], y_train)
    print("Fitted Isotonic Probability Calibrator on training OOF predictions.")

    # Evaluate Calibrated Champion on Validation Split
    raw_val_probs = champion_model.predict_proba(X_val)
    cal_val_probs = calibrator.calibrate(raw_val_probs)
    cal_val_pred = np.argmax(cal_val_probs, axis=1)

    champ_summary, champ_cm = ModelEvaluator.evaluate(
        model_id=champion_id,
        model_name=f"{champion_model.model_name}_Calibrated",
        y_true=y_val,
        y_pred=cal_val_pred,
        y_prob=cal_val_probs,
        split_name="validation",
    )
    print(f"Calibrated Champion Validation ECE: {champ_summary.expected_calibration_error:.4f} (Raw: {best_row['expected_calibration_error']})")

    # Export results
    results_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/development_results")
    results_dir.mkdir(parents=True, exist_ok=True)
    models_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/models")
    models_dir.mkdir(parents=True, exist_ok=True)

    df_comp.to_csv(results_dir / "model_comparison.csv", index=False)
    df_comp.to_csv(Path("docs/stage22_model_comparison.csv"), index=False)
    champ_cm.to_csv(results_dir / "confusion_matrix.csv")

    # Error analysis export
    error_records = []
    for i, rec in enumerate(val_records):
        actual_label = INV_LABEL_MAP[y_val[i]]
        pred_label = INV_LABEL_MAP[cal_val_pred[i]]
        is_error = actual_label != pred_label
        error_records.append({
            "text_instance_id": rec["text_instance_id"],
            "actual_difficulty": actual_label,
            "predicted_difficulty": pred_label,
            "prob_easy": round(cal_val_probs[i, 0], 4),
            "prob_medium": round(cal_val_probs[i, 1], 4),
            "prob_hard": round(cal_val_probs[i, 2], 4),
            "is_error": is_error,
            "is_hard_to_easy_error": (actual_label == "hard" and pred_label == "easy"),
        })

    df_errors = pd.DataFrame(error_records)
    df_errors.to_csv(results_dir / "error_analysis.csv", index=False)

    # Save Champion Model and Calibrator
    joblib.dump(champion_model, models_dir / "selected_model.joblib")
    joblib.dump(calibrator, models_dir / "calibration_model.joblib")

    print(f"\nSaved models and evaluation benchmarks to {results_dir} and {models_dir}")


if __name__ == "__main__":
    main()
