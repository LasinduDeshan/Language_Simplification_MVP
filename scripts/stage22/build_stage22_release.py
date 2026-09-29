"""Step 5: Package release artifacts, compute SHA-256 manifest, and generate completion reports."""

import sys
import hashlib
import json
from pathlib import Path
import pandas as pd

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from app.complexity_analysis.repositories.model_repository import ModelRepository
from app.complexity_analysis.repositories.feature_repository import FeatureRepository
from app.complexity_analysis.repositories.label_repository import LabelRepository
from app.complexity_analysis.pipeline import ComplexityAnalysisPipeline
from app.complexity_analysis.version import (
    STAGE22_CLASSIFIER_VERSION,
    STAGE22_FEATURE_SCHEMA_VERSION,
    STAGE22_PIPELINE_VERSION,
    STAGE22_PREPROCESSING_VERSION,
    STAGE22_SOURCE_DATASET_VERSION,
)


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    base_dir = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0")
    models_dir = base_dir / "models"
    manifests_dir = base_dir / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load model package & create pipeline
    model_repo = ModelRepository(models_dir=models_dir)
    pkg = model_repo.load_package()

    pipeline = ComplexityAnalysisPipeline(
        classifier=pkg["classifier"],
        feature_builder=pkg["feature_builder"],
        calibrator=pkg["calibrator"],
        ood_detector=pkg["ood_detector"],
    )

    # 2. Run inference on validation split
    feat_repo = FeatureRepository()
    df_feats = feat_repo.load_features_df()
    val_records = df_feats[df_feats["dataset_split"] == "development_candidate_validation"].to_dict(orient="records")

    print(f"Running inference on {len(val_records)} validation split records...")
    val_results = pipeline.classify_batch(val_records)

    val_json_path = base_dir / "development_results" / "validation_predictions.json"
    with open(val_json_path, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in val_results], f, indent=2)

    # 3. Generate SHA-256 Manifest
    manifest_lines = []
    manifest_dict = {}

    all_files = sorted(list(base_dir.rglob("*")))
    for p in all_files:
        if p.is_file() and not p.name.endswith(".sha256") and not p.name.endswith("run_manifest.json"):
            rel_path = p.relative_to(base_dir).as_posix()
            h = compute_sha256(p)
            manifest_lines.append(f"{h}  {rel_path}")
            manifest_dict[rel_path] = {
                "sha256": h,
                "size_bytes": p.stat().st_size,
            }

    manifest_sha256_path = manifests_dir / "stage22_manifest.sha256"
    with open(manifest_sha256_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    docs_sha256_path = Path("docs/stage22_manifest.sha256")
    with open(docs_sha256_path, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines) + "\n")

    run_manifest = {
        "stage": "stage_22_english_complexity_analysis",
        "pipeline_version": STAGE22_PIPELINE_VERSION,
        "classifier_version": STAGE22_CLASSIFIER_VERSION,
        "feature_schema_version": STAGE22_FEATURE_SCHEMA_VERSION,
        "source_dataset_version": STAGE22_SOURCE_DATASET_VERSION,
        "preprocessing_pipeline_version": STAGE22_PREPROCESSING_VERSION,
        "model_status": "provisional_label_pilot",
        "ground_truth_status": "not_expert_validated",
        "approved_for_child_delivery": False,
        "research_eligible": False,
        "production_inference_enabled": False,
        "primary_tier1_training_gate": "NOT PASSED",
        "primary_tier1_gate_reason": "0 expert_verified or reviewer_consensus labels",
        "secondary_pilot_gate": "PASSED",
        "pilot_labels_available": 1440,
        "pilot_labels_eligible_after_exclusions": 1430,
        "governance_status": {
            "model_status": "provisional_label_pilot",
            "ground_truth_status": "not_expert_validated",
            "approved_for_child_delivery": False,
            "research_eligible": False,
            "production_inference_enabled": False,
            "requires_expert_validation": True,
        },
        "total_files": len(manifest_dict),
        "files": manifest_dict,
    }

    with open(manifests_dir / "run_manifest.json", "w", encoding="utf-8") as f:
        json.dump(run_manifest, f, indent=2)

    print(f"Generated SHA-256 manifest ({len(manifest_dict)} files tracked).")

    # 4. Generate Completion Record
    comp_record_md = """# Stage 22 Completion Record — English Complexity Analysis and Difficulty Classification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** English educational content for children aged 4–8  
**Release Version:** `classifier-1.0.0` (Source: `0.2.0`, Preprocessing: `1.0.0`)  
**Stage Characterization:** Stage 22 completed as an internal pilot complexity classifier  
**Governance Status:**  
- `model_status = "provisional_label_pilot"`  
- `ground_truth_status = "not_expert_validated"`  
- `approved_for_child_delivery = false`  
- `research_eligible = false`  
- `production_inference_enabled = false`  
- `requires_expert_validation = true`  
**Status:** COMPLETE & SEALED (INTERNAL PILOT ONLY)  

---

## 1. Executive Summary

Stage 22 has developed, trained, calibrated, and released an internal pilot complexity classifier and feature analysis pipeline. It classifies educational text into three discrete linguistic complexity tiers:
- `easy`: Low lexical and syntactic complexity, short structures, limited relational or instructional load.
- `medium`: Moderate vocabulary, sentence structure, clause complexity, and instructional load.
- `hard`: High lexical, syntactic, or semantic-processing complexity, such as advanced vocabulary, embedded clauses, multiple relations, or multi-step load.

The trained B0–B5 models are secondary pilot models trained to reproduce provisional author labels—not validated difficulty classifiers.

The system strictly enforces responsibility boundaries:
- Zero clinical or DLD screening diagnosis claims.
- Read-only screening risk level exclusion.
- Complete isolation from learner profile personalization.

---

## 2. Gate Verification & Governance Disposition

### 2.1 Primary vs. Secondary Gate Disposition
- **Primary Tier-1 Training Gate:** **NOT PASSED**  
  - **Reason:** 0 `expert_verified` or `reviewer_consensus` labels exist in the corpus.
- **Secondary Provisional-Label Pilot Gate:** **PASSED**  
  - **Pilot Labels Available:** 1,440  
  - **Pilot Labels Eligible After Higher-Precedence Exclusions:** 1,430  

### 2.2 Recharacterization of Model Results
B5 achieved a provisional-label internal validation Macro-F1 of 0.9696. This measures agreement with draft authoring labels and does not demonstrate agreement with expert judgement or child suitability.

```json
{
  "model_status": "provisional_label_pilot",
  "ground_truth_status": "not_expert_validated",
  "approved_for_child_delivery": false,
  "research_eligible": false,
  "production_inference_enabled": false
}
```

---

## 3. Governed Accounting Reconciliations

### 3.1 Parent-Record Accounting (2,050 Cumulative Parents)
$$\\text{Cumulative Governed Parents (2,050)} = \\text{Directly Ingested Stage 21 Parents (1,980)} + \\text{Legacy Source Parents (70)}$$

- Cumulative Governed Parents: **2,050** ($370\\text{ Sources} + 1,110\\text{ Pairs} + 192\\text{ Activities} + 378\\text{ Lexicons}$)
- Directly Ingested Stage 21 Parents: **1,980** ($300\\text{ Sources} + 1,110\\text{ Pairs} + 192\\text{ Activities} + 378\\text{ Lexicons}$)
- Legacy Source Parents Not Directly Adapted: **70**
- Legacy Source Texts Preserved Through Pairs: **70/70**
- Unaccounted Governed Parents: **0**

### 3.2 Text-Instance Mutually Exclusive Accounting (3,617 Text Instances)
Every extracted text instance received exactly one primary disposition via the 9-step precedence order:

| Precedence Step | Primary Disposition | Count | Percentage | Description |
|:---:|---|---:|---:|---|
| 1 | `locked_test` | 315 | 8.71% | Quarantined candidate test split |
| 2 | `adaptation_test_excluded` | 377 | 10.42% | Adaptation activities excluded from training |
| 3 | `preprocessing_failed` | 0 | 0.00% | Zero NLP preprocessing failures |
| 4 | `stage21_manual_review` | 154 | 4.26% | Stage 21 function-word density reviews (9 in locked/adapt) |
| 5 | `missing_or_conflicting_label` | 1,341 | 37.07% | Lexicon entries & unannotated simplified texts |
| 6 | `provisional_secondary_only` | 1,430 | 39.54% | Draft authoring items awaiting expert annotation (10 in review) |
| 7 | `rule_seeded_audit_only` | 0 | 0.00% | Heuristic labels (audit only) |
| 8 | `primary_train_eligible` | 0 | 0.00% | Formal Tier 1 labels (pending expert panel) |
| 9 | `primary_validation_eligible` | 0 | 0.00% | Formal Tier 1 labels (pending expert panel) |
| **Total** | **All Governed Text Instances** | **3,617** | **100.00%** | **Zero-Loss Accounting Verified** |

---

## 4. Label Provenance Audit & Pilot Sufficiency

- **Draft Label Origin:** All 1,440 draft difficulty labels originated from research team authoring in Stage 20 (`validation_status: "draft"`, `requires_expert_review: true`).
- **Classification:** Strictly audited and classified as **`provisional`** (Tier 2 authoring draft labels). Zero provisional labels were promoted to Tier 1 ground truth.
- **Pilot Sufficiency:** Smallest class contains 9 independent source groups ($9 \\ge 3$ valid folds supported for pilot evaluation).
- **Provenance Columns Recorded:** `text_instance_id`, `difficulty_label`, `label_status`, `reviewer_reference`, `reviewer_role`, `annotation_guideline_version`, `reviewed_at`, `agreement_status`, `adjudication_status`.

---

## 5. Model Comparison & Champion Selection

All 6 candidate architectures were evaluated on the provisional-label validation split:

| Model ID | Architecture | Provisional-Label Validation Macro-F1 | Balanced Accuracy | Raw ECE | Calibrated ECE (Exploratory) |
|---|---|---:|---:|---:|---:|
| **B0** | Majority Baseline | 0.2121 | 0.3333 | 0.0374 | N/A |
| **B1** | Transparent Rule Baseline | 0.2352 | 0.5362 | 0.4178 | N/A |
| **B2** | Multinomial Logistic Regression | 0.9089 | 0.9089 | 0.0962 | 0.0412 |
| **B3** | Constrained Decision Tree | 0.6144 | 0.6218 | 0.0380 | 0.0365 |
| **B4** | Random Forest Classifier | 0.9696 | 0.9696 | 0.1099 | 0.0353 |
| **B5** | HistGradientBoosting Classifier | **0.9696** | **0.9696** | **0.0404** | **0.0353** |

### Formally Selected Champion Model: B5 (`HistGradientBoostingComplexityClassifier`)
- **Selected Champion:** `HistGradientBoostingComplexityClassifier` (B5)
- **Selection Reason:** Achieved the highest internal validation Macro-F1 among the evaluated Stage 22 candidates with numerically lower raw ECE (0.0404 vs 0.1099 for B4), compact memory footprint (87.4 KB), fast inference latency (<0.05 ms/item), and native handling of tabular continuous features.
- **Difference from B2 (Linear Baseline):** +0.0634 Macro-F1.
- **Uncertainty Interval (Paired Bootstrap 95% CI vs B2):** $[0.0308, 0.1037]$ (statistically significant difference against linear baseline on provisional labels).
- **Probability Calibration Method:** Exploratory Isotonic Regression fitted strictly on training out-of-fold predictions (labelled exploratory due to limited independent group count).
- **Hyperparameters:** `max_iter=100`, `max_depth=5`, `min_samples_leaf=5`, `learning_rate=0.08`, `l2_regularization=0.1`.
- **Random Seed:** 42.

---

## 6. Safety-Critical Error Analysis

- **Observed Hard $\\to$ Easy Misclassifications:** 0 / 15 actual hard validation instances.
- **Observed Rate:** 0.00%.
- **95% Wilson Score Binomial CI:** $[0.0000, 0.2041]$.
- **Safety Target Statistically Demonstrated:** No.
- **Safety Evaluation Statement:** No Hard $\\to$ Easy errors were observed in the small validation sample ($0/15$). However, the 95% Wilson upper bound was 20.41%; therefore, the $\\le 2\\%$ safety target was not statistically demonstrated and requires a larger expert-labelled evaluation set. Do not use the observed 0% as evidence of deployment safety.

---

## 7. Governed Release Manifest

Release root: `data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/`  
SHA-256 Manifest: `manifests/stage22_manifest.sha256`
"""

    summary_path = base_dir / "reports" / "complexity_release_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(comp_record_md)

    docs_completion_path = Path("docs/stage22_completion_record.md")
    with open(docs_completion_path, "w", encoding="utf-8") as f:
        f.write(comp_record_md)

    print(f"Exported release summary to {summary_path} and {docs_completion_path}")


if __name__ == "__main__":
    main()
