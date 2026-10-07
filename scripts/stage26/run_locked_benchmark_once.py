"""
Stage 26 WP9: Single Frozen Locked Benchmark Evaluation.
Reports dual benchmark views:
1. Full Historical Locked Benchmark (45 source groups -> 135 pairs)
2. Clean Text-Simplification Subset (13 clean source groups -> 39 pairs)
Enforces invalid execution abort policy and records non-reconstructable metrics.
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
from app.model_simplification.adapters.gemini_adapter import GeminiModelAdapter
from app.model_simplification.adapters.mt5_adapter import MT5ModelAdapter
from app.model_simplification.adapters.mbart_adapter import MBARTModelAdapter
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.datasets.external_english.benchmark.metrics import compute_sari, estimate_fkgl
import sacrebleu


def evaluate_dataset_subset(
    adapter_or_router,
    items: List[Dict[str, Any]],
    model_id: str,
    view_name: str,
) -> Dict[str, Any]:
    start_time = time.perf_counter()
    results = []
    sari_scores = []
    bleu_preds = []
    bleu_refs = []
    fkgl_deltas = []
    outcome_counts = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}
    total_cost = 0.0

    for item in items:
        source_text = item.get("source_text") or item.get("text", "")
        tier = item.get("support_level", "moderate").lower()
        target_age = item.get("target_age", 6)
        protected = item.get("protected_terms", [])
        refs = item.get("reference_texts", [item.get("target_text", source_text)])

        req = ModelGenerationRequest(
            request_id=f"LOCKED-{model_id[:6]}-{len(results)+1}",
            text=source_text,
            support_level=tier,
            target_age=target_age,
            protected_elements=ProtectedElementsDTO(exact_preservation=protected),
        )

        if hasattr(adapter_or_router, "route_and_generate"):
            res = adapter_or_router.route_and_generate(req, model_id=model_id)
        else:
            res = adapter_or_router.generate(req)

        cat, provider = ProviderResultAttribution.classify_outcome(res)
        outcome_counts[cat] += 1
        total_cost += (res.estimated_cost or 0.0)

        cand = res.candidate_text or source_text

        # Compute SARI against references
        sari_val, sari_add, sari_keep, sari_del = compute_sari(source_text, cand, refs)
        sari_scores.append(sari_val)

        bleu_preds.append(cand)
        bleu_refs.append(refs)

        # FKGL
        orig_fkgl = estimate_fkgl(source_text)
        out_fkgl = estimate_fkgl(cand)
        fkgl_deltas.append(orig_fkgl - out_fkgl)

        results.append({
            "request_id": req.request_id,
            "source_text": source_text,
            "candidate_text": cand,
            "tier": tier,
            "accounting_outcome": cat,
            "effective_provider": provider,
            "execution_status": res.execution_status.value,
            "fallback_used": res.fallback_used,
            "latency_ms": res.latency_ms,
            "cost": res.estimated_cost,
        })

    # Corpus BLEU
    max_refs = max(len(r) for r in bleu_refs) if bleu_refs else 1
    ref_streams = []
    for r_idx in range(max_refs):
        stream = [r[r_idx] if r_idx < len(r) else r[0] for r in bleu_refs]
        ref_streams.append(stream)

    corpus_bleu = sacrebleu.corpus_bleu(bleu_preds, ref_streams).score if bleu_preds else 0.0

    mean_sari = float(sum(sari_scores) / max(1, len(sari_scores)))
    mean_fkgl_delta = float(sum(fkgl_deltas) / max(1, len(fkgl_deltas)))
    total_latency = (time.perf_counter() - start_time) * 1000.0
    mean_latency = total_latency / max(1, len(items))

    summary = {
        "model_id": model_id,
        "benchmark_view": view_name,
        "total_samples": len(items),
        "mean_sari": round(mean_sari, 2),
        "corpus_bleu": round(corpus_bleu, 2),
        "mean_fkgl_delta": round(mean_fkgl_delta, 2),
        "mean_latency_ms": round(mean_latency, 2),
        "total_cost": round(total_cost, 6),
        "outcome_breakdown": outcome_counts,
        "pass_rate": round((outcome_counts[ProviderResultAttribution.CAT_NATIVE_DELIVERED] + outcome_counts[ProviderResultAttribution.CAT_REPAIR_DELIVERED]) / max(1, len(items)), 4),
        "fallback_rate": round(outcome_counts[ProviderResultAttribution.CAT_FALLBACK_DELIVERED] / max(1, len(items)), 4),
        "manual_review_rate": round(outcome_counts[ProviderResultAttribution.CAT_MANUAL_REVIEW] / max(1, len(items)), 4),
        "rejection_rate": round(outcome_counts[ProviderResultAttribution.CAT_REJECTED] / max(1, len(items)), 4),
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }
    return summary, results


def main():
    inputs_dir = repo_root / "data" / "baseline_simplification" / "evaluation_inputs"
    locked_test_file = inputs_dir / "internal_locked_test_groups.json"
    manifest_path = repo_root / "data" / "model_simplification" / "registry" / "stage26_training_eligibility_manifest.json"

    if not locked_test_file.exists():
        print(f"[-] Locked test file {locked_test_file} not found.")
        return

    with open(locked_test_file, "r", encoding="utf-8") as f:
        locked_groups = json.load(f)

    # 1. Full Locked Benchmark items (45 groups x 3 tiers = 135 items)
    full_items = []
    for g in locked_groups:
        for t in ["mild", "moderate", "strong"]:
            full_items.append({
                "source_group_id": g.get("source_group_id"),
                "source_text": g["source_text"],
                "support_level": t,
                "target_age": 6,
                "protected_terms": g.get("protected_terms", []),
                "reference_texts": g.get("reference_texts", [g["source_text"]]),
            })

    # 2. Clean Text-Simplification Subset items (Exclude contaminated groups)
    with open(repo_root / "data" / "simplification_corpus" / "releases" / "0.2.0" / "dataset_issue_register.json", "r", encoding="utf-8") as f:
        register = json.load(f)
    flagged_sources = {item.get("source_item_id") for item in register.get("flagged_records", []) if item.get("source_item_id")}

    clean_items = [item for item in full_items if item.get("source_group_id") not in flagged_sources]

    out_dir = repo_root / "data" / "model_simplification" / "results" / "locked_test"
    out_dir.mkdir(parents=True, exist_ok=True)

    models_to_evaluate = [
        ("stage25-controlled-deterministic", Stage25ControlledAdapter()),
        ("mt5-base-zero-shot", MT5ModelAdapter(mode="pretrained_zero_shot")),
        ("mbart-large-50-zero-shot", MBARTModelAdapter(mode="pretrained_zero_shot")),
        ("gemini-1.5-flash-prompted", ModelRouter()),
        ("hybrid-gemini-stage25-validated", ModelRouter()),
    ]

    dual_results = {
        "full_historical_locked_set": {},
        "clean_text_simplification_subset": {},
    }

    print("=" * 65)
    print("STAGE 26 DUAL LOCKED BENCHMARK RUNNER")
    print(f"  Full Locked Benchmark Items: {len(full_items)} (45 groups)")
    print(f"  Clean Subset Benchmark Items: {len(clean_items)} ({len(clean_items)//3} groups)")
    print("=" * 65)

    for model_id, runner_instance in models_to_evaluate:
        print(f"\n[*] Evaluating {model_id}...")
        
        # Run Full Set
        full_summary, full_recs = evaluate_dataset_subset(runner_instance, full_items, model_id, "full_historical_locked_set")
        dual_results["full_historical_locked_set"][model_id] = full_summary
        print(f"    [Full Set]  SARI: {full_summary['mean_sari']:.2f} | BLEU: {full_summary['corpus_bleu']:.2f} | Pass: {full_summary['pass_rate']*100:.1f}%")

        # Run Clean Subset
        clean_summary, clean_recs = evaluate_dataset_subset(runner_instance, clean_items, model_id, "clean_text_simplification_subset")
        dual_results["clean_text_simplification_subset"][model_id] = clean_summary
        print(f"    [Clean Sub] SARI: {clean_summary['mean_sari']:.2f} | BLEU: {clean_summary['corpus_bleu']:.2f} | Pass: {clean_summary['pass_rate']*100:.1f}%")

    out_summary_file = out_dir / "stage26_dual_locked_benchmark_summary.json"
    with open(out_summary_file, "w", encoding="utf-8") as f:
        json.dump(dual_results, f, indent=2)

    print("\n" + "=" * 65)
    print(f"[+] Dual locked benchmark summary saved to: {out_summary_file}")
    print("=" * 65)


if __name__ == "__main__":
    main()
