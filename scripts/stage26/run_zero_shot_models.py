"""
Stage 26 WP5 & WP8: Run Zero-Shot and Prompted Local Transformer Models on Internal Validation & Locked Splits.
Evaluates mT5, mBART, and Stage 25 deterministic comparator.
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
from app.model_simplification.adapters.mt5_adapter import MT5ModelAdapter
from app.model_simplification.adapters.mbart_adapter import MBARTModelAdapter
from app.model_simplification.adapters.stage25_adapter import Stage25ControlledAdapter
from app.model_simplification.provider_result_attribution import ProviderResultAttribution
from app.datasets.external_english.benchmark.metrics import compute_sari, estimate_fkgl
import sacrebleu


def evaluate_adapter_on_split(adapter, items: List[Dict[str, Any]], model_id: str, split_name: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    results = []
    sari_scores = []
    bleu_preds = []
    bleu_refs = []
    fkgl_deltas = []
    outcome_counts = {cat: 0 for cat in ProviderResultAttribution.ALL_CATEGORIES}

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

        res = adapter.generate(req)
        cat, provider = ProviderResultAttribution.classify_outcome(res)
        outcome_counts[cat] += 1

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
        })

    # Corpus BLEU
    # Sacrebleu expects refs as list of ref-streams
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

    # Flatten validation groups into tier items
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

    adapters = [
        ("stage25-controlled-deterministic", Stage25ControlledAdapter()),
        ("mt5-base-zero-shot", MT5ModelAdapter(mode="pretrained_zero_shot")),
        ("mbart-large-50-zero-shot", MBARTModelAdapter(mode="pretrained_zero_shot")),
    ]

    all_summaries = {}
    for model_id, adapter in adapters:
        print(f"[*] Evaluating {model_id} on validation split ({len(eval_items)} items)...")
        summary, recs = evaluate_adapter_on_split(adapter, eval_items, model_id, "validation")
        all_summaries[model_id] = summary
        print(f"    SARI: {summary['mean_sari']:.2f} | BLEU: {summary['corpus_bleu']:.2f} | Pass Rate: {summary['pass_rate']*100:.1f}% | Fallback: {summary['fallback_rate']*100:.1f}%")

    with open(out_dir / "zero_shot_and_stage25_validation_summary.json", "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)

    print(f"[+] Validation evaluation saved to: {out_dir / 'zero_shot_and_stage25_validation_summary.json'}")


if __name__ == "__main__":
    main()
