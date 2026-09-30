"""
Baseline Evaluator computing SARI, BLEU, FKGL reduction, safety preservation, and operational metrics.
"""
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import sacrebleu
from app.datasets.external_english.benchmark.metrics import (
    compute_sari,
    estimate_fkgl,
    tokenize_words,
)
from app.baseline_simplification.schemas import BaselineOutputRecord, FinalDisposition

class BaselineEvaluator:
    """Computes reference-based simplification, readability, and operational metrics for a baseline run."""

    def __init__(self):
        pass

    def evaluate_dataset_outputs(
        self,
        records: List[BaselineOutputRecord],
        ground_truth_map: Dict[str, Dict[str, Any]], # source_group_id -> { "orig": str, "refs": List[str] }
    ) -> Dict[str, Any]:
        """Evaluates a list of BaselineOutputRecord items against multi-reference ground truth."""
        if not records:
            return {"error": "No records provided for evaluation"}

        eligible_records = [r for r in records if r.metric_eligibility]
        
        sari_scores = []
        sari_add_scores = []
        sari_keep_scores = []
        sari_del_scores = []
        
        preds_for_bleu = []
        refs_for_bleu: List[List[str]] = []
        
        orig_fkgls = []
        out_fkgls = []
        fkgl_deltas = []
        
        word_compressions = []
        char_compressions = []
        
        latencies = []
        passed_count = 0
        manual_review_count = 0
        failed_count = 0
        quarantined_count = 0

        for rec in records:
            latencies.append(rec.latency_ms)
            if rec.quality_disposition == FinalDisposition.AUTOMATIC_CHECK_PASSED:
                passed_count += 1
            elif rec.quality_disposition == FinalDisposition.MANUAL_REVIEW_REQUIRED:
                manual_review_count += 1
            elif rec.quality_disposition == FinalDisposition.AUTOMATIC_CHECK_FAILED:
                failed_count += 1
            elif rec.quality_disposition == FinalDisposition.QUARANTINED:
                quarantined_count += 1

            # Only compute reference metrics if eligible and present in ground truth
            group_id = rec.source_group_id
            if rec.metric_eligibility and group_id in ground_truth_map:
                gt = ground_truth_map[group_id]
                orig_text = gt["orig"]
                ref_texts = gt["refs"]
                pred_text = rec.output_text

                # 1. SARI
                sari, s_add, s_keep, s_del = compute_sari(orig_text, pred_text, ref_texts)
                sari_scores.append(sari)
                sari_add_scores.append(s_add)
                sari_keep_scores.append(s_keep)
                sari_del_scores.append(s_del)

                # 2. Collect for Corpus BLEU
                preds_for_bleu.append(pred_text)

                # 3. Readability & FKGL
                orig_fk = estimate_fkgl(orig_text)
                out_fk = estimate_fkgl(pred_text)
                orig_fkgls.append(orig_fk)
                out_fkgls.append(out_fk)
                fkgl_deltas.append(orig_fk - out_fk)

                # 4. Compression
                orig_words = len(tokenize_words(orig_text))
                pred_words = len(tokenize_words(pred_text))
                w_ratio = (pred_words / orig_words) if orig_words > 0 else 1.0
                word_compressions.append(w_ratio)

                c_ratio = (len(pred_text) / len(orig_text)) if len(orig_text) > 0 else 1.0
                char_compressions.append(c_ratio)

        # Build refs_for_bleu matrix: List of reference streams (stream 0 = ref 0 for all items, stream 1 = ref 1, ...)
        if eligible_records:
            max_refs = max(len(ground_truth_map[r.source_group_id]["refs"]) for r in eligible_records if r.source_group_id in ground_truth_map)
            refs_for_bleu = [[] for _ in range(max_refs)]
            for r in eligible_records:
                if r.source_group_id in ground_truth_map:
                    r_list = ground_truth_map[r.source_group_id]["refs"]
                    for ref_idx in range(max_refs):
                        ref_val = r_list[ref_idx] if ref_idx < len(r_list) else r_list[-1]
                        refs_for_bleu[ref_idx].append(ref_val)

        corpus_bleu_score = 0.0
        if preds_for_bleu and refs_for_bleu:
            try:
                bleu_res = sacrebleu.corpus_bleu(preds_for_bleu, refs_for_bleu)
                corpus_bleu_score = float(bleu_res.score)
            except Exception as e:
                corpus_bleu_score = 0.0

        return {
            "total_records": len(records),
            "eligible_records": len(eligible_records),
            "dispositions": {
                "automatic_check_passed": passed_count,
                "manual_review_required": manual_review_count,
                "automatic_check_failed": failed_count,
                "quarantined": quarantined_count,
            },
            "metrics": {
                "sari": {
                    "mean": float(np.mean(sari_scores)) if sari_scores else 0.0,
                    "std": float(np.std(sari_scores)) if sari_scores else 0.0,
                    "median": float(np.median(sari_scores)) if sari_scores else 0.0,
                },
                "sari_add": float(np.mean(sari_add_scores)) if sari_add_scores else 0.0,
                "sari_keep": float(np.mean(sari_keep_scores)) if sari_keep_scores else 0.0,
                "sari_del": float(np.mean(sari_del_scores)) if sari_del_scores else 0.0,
                "corpus_bleu": corpus_bleu_score,
                "fkgl": {
                    "original_mean": float(np.mean(orig_fkgls)) if orig_fkgls else 0.0,
                    "output_mean": float(np.mean(out_fkgls)) if out_fkgls else 0.0,
                    "reduction_delta": float(np.mean(fkgl_deltas)) if fkgl_deltas else 0.0,
                },
                "compression": {
                    "word_ratio": float(np.mean(word_compressions)) if word_compressions else 1.0,
                    "char_ratio": float(np.mean(char_compressions)) if char_compressions else 1.0,
                },
            },
            "operational": {
                "mean_latency_ms": float(np.mean(latencies)) if latencies else 0.0,
                "median_latency_ms": float(np.median(latencies)) if latencies else 0.0,
                "p95_latency_ms": float(np.percentile(latencies, 95)) if latencies else 0.0,
                "throughput_samples_per_sec": (1000.0 / float(np.mean(latencies))) if latencies and np.mean(latencies) > 0 else 0.0,
            },
        }
