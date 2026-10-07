"""
Stage 24: Run baseline evaluations on official ASSET test set (359 groups -> 359 outputs/baseline).
Evaluates B0-B5 against 10 references each using automated mode.
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
    out_dir = repo_root / "data" / "baseline_simplification" / "results" / "asset"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(inputs_dir / "asset_test_groups.json", "r", encoding="utf-8") as f:
        asset_groups = json.load(f)

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

    asset_gt = {g["source_group_id"]: {"orig": g["source_text"], "refs": g["reference_texts"]} for g in asset_groups}

    asset_summary = {}
    all_asset_records = []

    print("=== Running ASSET Benchmark Evaluation (359 groups) ===")
    for m in methods:
        run_id = f"BASE-ASSET-TEST-{m.value}-20260930"
        records = runner.run_on_items(
            method_id=m,
            items=asset_groups,
            dataset_id="asset",
            dataset_version="0.1.0",
            split="test",
            run_id=run_id,
            validation_mode=ProtectedElementSource.AUTOMATED_EXTRACTOR_ONLY,
            target_age_default=6,
        )
        eval_res = evaluator.evaluate_dataset_outputs(records, asset_gt)
        asset_summary[m.value] = eval_res
        all_asset_records.extend(records)
        print(f"[{m.value}] ASSET SARI: {eval_res['metrics']['sari']['mean']:.2f} | BLEU: {eval_res['metrics']['corpus_bleu']:.2f} | FKGL Delta: {eval_res['metrics']['fkgl']['reduction_delta']:.2f}")

    with open(out_dir / "asset_benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(asset_summary, f, indent=2)

    with open(out_dir / "asset_test_records.jsonl", "w", encoding="utf-8") as f:
        for r in all_asset_records:
            f.write(r.model_dump_json() + "\n")

    print(f"\nCompleted! Total ASSET Test Outputs across B0-B5: {len(all_asset_records)} (Expected: 2,154)")

if __name__ == "__main__":
    main()
