"""
Stage 24: Run baseline evaluations on Internal English Corpus (Release 0.2.0).
Executes B0-B5 on Validation split and Locked Test split (45 groups -> 45 outputs/baseline -> 270 total).
"""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

import json
from typing import Any, Dict, List
from app.baseline_simplification.schemas import (
    BaselineMethodId,
    ProtectedElementSource,
)
from app.baseline_simplification.runner import BaselineRunner
from app.baseline_simplification.evaluator import BaselineEvaluator

def main():
    inputs_dir = repo_root / "data" / "baseline_simplification" / "evaluation_inputs"
    out_dir = repo_root / "data" / "baseline_simplification" / "results" / "internal"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(inputs_dir / "internal_validation_groups.json", "r", encoding="utf-8") as f:
        val_groups = json.load(f)
    with open(inputs_dir / "internal_locked_test_groups.json", "r", encoding="utf-8") as f:
        locked_test_groups = json.load(f)

    runner = BaselineRunner()
    evaluator = BaselineEvaluator()

    methods = [
        BaselineMethodId.B0,
        BaselineMethodId.B1,
        BaselineMethodId.B2,
        BaselineMethodId.B3,
        BaselineMethodId.B4,
        BaselineMethodId.B5,
    ]

    # Ground truth maps for multi-reference evaluation
    val_gt = {g["source_group_id"]: {"orig": g["source_text"], "refs": g["reference_texts"]} for g in val_groups}
    test_gt = {g["source_group_id"]: {"orig": g["source_text"], "refs": g["reference_texts"]} for g in locked_test_groups}

    val_summary = {}
    test_summary = {}
    all_test_records = []

    print("=== Running Internal Validation Split (45 groups) ===")
    for m in methods:
        run_id = f"BASE-INT-VAL-{m.value}-20260930"
        records = runner.run_on_items(
            method_id=m,
            items=val_groups,
            dataset_id="internal_english",
            dataset_version="0.2.0",
            split="development_candidate_validation",
            run_id=run_id,
            validation_mode=ProtectedElementSource.GOVERNED_ANNOTATIONS_PLUS_EXTRACTOR,
        )
        eval_res = evaluator.evaluate_dataset_outputs(records, val_gt)
        val_summary[m.value] = eval_res
        print(f"[{m.value}] Val SARI: {eval_res['metrics']['sari']['mean']:.2f} | BLEU: {eval_res['metrics']['corpus_bleu']:.2f} | FKGL Delta: {eval_res['metrics']['fkgl']['reduction_delta']:.2f}")

    print("\n=== Running Internal Locked Test Split (45 groups -> 270 total outputs) ===")
    for m in methods:
        run_id = f"BASE-INT-TEST-{m.value}-20260930"
        records = runner.run_on_items(
            method_id=m,
            items=locked_test_groups,
            dataset_id="internal_english",
            dataset_version="0.2.0",
            split="development_candidate_test",
            run_id=run_id,
            validation_mode=ProtectedElementSource.GOVERNED_ANNOTATIONS_PLUS_EXTRACTOR,
        )
        eval_res = evaluator.evaluate_dataset_outputs(records, test_gt)
        test_summary[m.value] = eval_res
        all_test_records.extend(records)
        print(f"[{m.value}] Test SARI: {eval_res['metrics']['sari']['mean']:.2f} | BLEU: {eval_res['metrics']['corpus_bleu']:.2f} | FKGL Delta: {eval_res['metrics']['fkgl']['reduction_delta']:.2f}")

    with open(out_dir / "internal_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(val_summary, f, indent=2)
    with open(out_dir / "internal_locked_test_summary.json", "w", encoding="utf-8") as f:
        json.dump(test_summary, f, indent=2)
        
    # Serialize non-reconstructable evaluation output metadata records
    with open(out_dir / "internal_locked_test_records.jsonl", "w", encoding="utf-8") as f:
        for r in all_test_records:
            f.write(r.model_dump_json() + "\n")

    print(f"\nCompleted! Total Locked Test Outputs across B0-B5: {len(all_test_records)} (Expected: 270)")

if __name__ == "__main__":
    main()
