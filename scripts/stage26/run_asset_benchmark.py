"""
Stage 26 WP9: ASSET External Benchmark Evaluation under Non-Commercial Research Policy.
Evaluates candidate models against external multi-reference benchmark ASSET.
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(repo_root / "backend"))

from app.model_simplification.schemas import (
    ModelGenerationRequest,
    ProtectedElementsDTO,
)
from app.model_simplification.router import ModelRouter
from app.model_simplification.adapters.stage25_adapter import Stage25ControlledAdapter
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.datasets.external_english.benchmark.metrics import compute_sari, estimate_fkgl
import sacrebleu


def main():
    asset_file = repo_root / "data" / "datasets" / "external_english" / "raw" / "asset" / "asset.test.json"
    if not asset_file.exists():
        # Check alternative path
        alt_paths = [
            repo_root / "data" / "external_english" / "asset_test.json",
            repo_root / "data" / "baseline_simplification" / "evaluation_inputs" / "asset_test_samples.json",
        ]
        for p in alt_paths:
            if p.exists():
                asset_file = p
                break

    out_dir = repo_root / "data" / "model_simplification" / "results" / "asset"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_doc = repo_root / "docs" / "stage26_asset_evaluation_report.md"

    if not asset_file.exists():
        # Record official NOT_EXECUTED status
        not_exec_md = f"""# Stage 26 ASSET External Benchmark Evaluation Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Status:** `NOT_EXECUTED`  
**Reason:** Raw ASSET test corpus asset.test.json not staged in local data directory.  
**Policy Compliance:** Stage 26 preserves strict boundary invariants; external benchmark evaluation is optional and non-blocking for internal locked benchmark freeze.
"""
        with open(out_doc, "w", encoding="utf-8") as f:
            f.write(not_exec_md)
        print(f"[+] ASSET report saved with NOT_EXECUTED status: {out_doc}")
        return

    # If ASSET dataset exists, evaluate
    with open(asset_file, "r", encoding="utf-8") as f:
        asset_data = json.load(f)

    # Process first 100 ASSET items for benchmark evaluation
    items = asset_data[:100] if isinstance(asset_data, list) else []
    print(f"[*] Loaded {len(items)} ASSET benchmark instances.")

    # Evaluate Stage 25 and Gemini Hybrid
    router = ModelRouter()
    models = [
        ("stage25-controlled-deterministic", Stage25ControlledAdapter()),
        ("hybrid-gemini-stage25-validated", router),
    ]

    asset_summary = {}
    for mid, runner_inst in models:
        sari_scores = []
        bleu_preds = []
        bleu_refs = []
        fkgl_deltas = []

        for item in items:
            orig = item.get("original") or item.get("source_text", "")
            refs = item.get("simplifications") or item.get("reference_texts", [orig])
            req = ModelGenerationRequest(
                request_id=f"ASSET-{mid[:6]}-{len(sari_scores)+1}",
                text=orig,
                support_level="moderate",
            )
            if hasattr(runner_inst, "route_and_generate"):
                res = runner_inst.route_and_generate(req, model_id=mid)
            else:
                res = runner_inst.generate(req)

            cand = res.candidate_text or orig
            sari_val, _, _, _ = compute_sari(orig, cand, refs)
            sari_scores.append(sari_val)
            bleu_preds.append(cand)
            bleu_refs.append(refs)
            fkgl_deltas.append(estimate_fkgl(orig) - estimate_fkgl(cand))

        max_refs = max(len(r) for r in bleu_refs) if bleu_refs else 1
        ref_streams = []
        for r_idx in range(max_refs):
            stream = [r[r_idx] if r_idx < len(r) else r[0] for r in bleu_refs]
            ref_streams.append(stream)

        corpus_bleu = sacrebleu.corpus_bleu(bleu_preds, ref_streams).score if bleu_preds else 0.0

        asset_summary[mid] = {
            "model_id": mid,
            "samples": len(items),
            "sari": round(sum(sari_scores)/max(1, len(sari_scores)), 2),
            "bleu": round(corpus_bleu, 2),
            "fkgl_delta": round(sum(fkgl_deltas)/max(1, len(fkgl_deltas)), 2),
        }

    with open(out_dir / "asset_benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(asset_summary, f, indent=2)

    report_md = f"""# Stage 26 ASSET External Benchmark Evaluation Report

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Status:** `COMPLETED`  
**Evaluated Instances:** {len(items)} ASSET Test Samples  
**Rights Policy:** Non-Commercial Academic Research Only  

---

## Benchmark Results

| Model ID | SARI Score | SacreBLEU | FKGL Delta |
| :--- | :---: | :---: | :---: |
"""
    for mid, res in asset_summary.items():
        report_md += f"| `{mid}` | **{res['sari']}** | **{res['bleu']}** | **{res['fkgl_delta']}** |\n"

    with open(out_doc, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"[+] ASSET evaluation complete and report saved: {out_doc}")


if __name__ == "__main__":
    main()
