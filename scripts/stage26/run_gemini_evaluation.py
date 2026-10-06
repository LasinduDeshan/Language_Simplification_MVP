"""
Stage 26 WP4 & WP8: Gemini and Hybrid Model Evaluation on Internal Validation Split.
Evaluates Gemini Prompted and Hybrid (Gemini + Stage 25 Deterministic Validator) on 135 validation items.
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
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.datasets.external_english.benchmark.metrics import compute_sari, estimate_fkgl
import sacrebleu


def evaluate_model_on_split(router: ModelRouter, items: List[Dict[str, Any]], model_id: str, split_name: str) -> Dict[str, Any]:
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
            request_id=f"REQ-{model_id[:6]}-{len(results)+1}",
            text=source_text,
            support_level=tier,
            target_age=target_age,
            protected_elements=ProtectedElementsDTO(exact_preservation=protected),
        )

        res = router.route_and_generate(req, model_id=model_id)
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
        "split": split_name,
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
    val_file = inputs_dir / "internal_validation_groups.json"

    if not val_file.exists():
        print(f"[-] Validation input file {val_file} not found.")
        return

    with open(val_file, "r", encoding="utf-8") as f:
        val_groups = json.load(f)

    eval_items = []
    for g in val_groups:
        for t in ["mild", "moderate", "strong"]:
            eval_items.append({
                "source_text": g["source_text"],
                "support_level": t,
                "target_age": 6,
                "protected_terms": g.get("protected_terms", []),
                "reference_texts": g.get("reference_texts", [g["source_text"]]),
            })

    out_dir = repo_root / "data" / "model_simplification" / "results" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)

    router = ModelRouter()
    
    # 1. Smoke test Gemini adapter
    print("[*] Running Gemini API discovery and smoke test...")
    ok, msg = router.gemini_adapter.discover_and_verify_model()
    print(f"    Discovery status: {ok} ({msg})")
    smoke_ok, smoke_msg = router.gemini_adapter.smoke_test()
    print(f"    Smoke test status: {smoke_ok} ({smoke_msg})")

    models_to_eval = [
        "gemini-1.5-flash-prompted",
        "hybrid-gemini-stage25-validated",
    ]

    all_summaries = {}
    for mid in models_to_eval:
        print(f"[*] Evaluating {mid} on validation split ({len(eval_items)} items)...")
        summary, recs = evaluate_model_on_split(router, eval_items, mid, "validation")
        all_summaries[mid] = summary
        print(f"    SARI: {summary['mean_sari']:.2f} | BLEU: {summary['corpus_bleu']:.2f} | Pass Rate: {summary['pass_rate']*100:.1f}% | Fallback: {summary['fallback_rate']*100:.1f}%")

    with open(out_dir / "gemini_and_hybrid_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)

    print(f"[+] Gemini validation evaluation saved to: {out_dir / 'gemini_and_hybrid_validation_summary.json'}")


if __name__ == "__main__":
    main()
