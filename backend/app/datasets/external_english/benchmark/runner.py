"""Benchmark runner executing baseline models on ASSET dataset and aggregating metrics."""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_bertscore_proxy,
    compute_complexity_reduction,
    compute_sari,
)
from app.datasets.external_english.benchmark.simplifiers import (
    GenericLLMSimplifier,
    IdentitySimplifier,
    RuleBasedSimplifier,
)
from app.datasets.external_english.schemas import NormalizedExternalRecord


class ASSETBenchmarkRunner:
    """Orchestrates benchmark evaluation of multiple simplification baselines on ASSET."""

    def __init__(self):
        self.simplifiers = {
            "identity": IdentitySimplifier(),
            "rule_based": RuleBasedSimplifier(),
            "generic_llm": GenericLLMSimplifier(),
        }

    def evaluate_split(
        self,
        records: List[NormalizedExternalRecord],
        split_name: str = "test",
    ) -> Dict[str, Any]:
        """Evaluates all registered baselines over a list of ASSET records."""
        results = {
            "split": split_name,
            "sample_count": len(records),
            "baselines": {},
        }

        for name, simplifier in self.simplifiers.items():
            sari_scores = []
            add_scores = []
            keep_scores = []
            del_scores = []
            bleu_scores = []
            bertscore_scores = []
            fkgl_reductions = []
            word_compressions = []
            latencies = []
            invalid_count = 0
            fallback_count = 0

            for rec in records:
                src = rec.evaluation_source_text
                refs = rec.evaluation_references

                pred, meta = simplifier.simplify(src)
                
                if not meta.get("is_valid", True):
                    invalid_count += 1
                if meta.get("is_fallback", False):
                    fallback_count += 1
                latencies.append(meta.get("latency_ms", 0.0))

                # Compute Metrics
                sari, add_s, keep_s, del_s = compute_sari(src, pred, refs)
                bleu = compute_bleu(pred, refs)
                bert = compute_bertscore_proxy(pred, refs)
                comp = compute_complexity_reduction(src, pred)

                sari_scores.append(sari)
                add_scores.append(add_s)
                keep_scores.append(keep_s)
                del_scores.append(del_s)
                bleu_scores.append(bleu)
                bertscore_scores.append(bert)
                fkgl_reductions.append(comp["fkgl_reduction"])
                word_compressions.append(comp["word_compression_ratio"])

            results["baselines"][name] = {
                "sari": {
                    "mean": float(np.mean(sari_scores)),
                    "std": float(np.std(sari_scores)),
                },
                "sari_add": {
                    "mean": float(np.mean(add_scores)),
                    "std": float(np.std(add_scores)),
                },
                "sari_keep": {
                    "mean": float(np.mean(keep_scores)),
                    "std": float(np.std(keep_scores)),
                },
                "sari_del": {
                    "mean": float(np.mean(del_scores)),
                    "std": float(np.std(del_scores)),
                },
                "bleu": {
                    "mean": float(np.mean(bleu_scores)),
                    "std": float(np.std(bleu_scores)),
                },
                "bertscore_proxy": {
                    "mean": float(np.mean(bertscore_scores)),
                    "std": float(np.std(bertscore_scores)),
                },
                "fkgl_reduction": {
                    "mean": float(np.mean(fkgl_reductions)),
                    "std": float(np.std(fkgl_reductions)),
                },
                "word_compression_ratio": {
                    "mean": float(np.mean(word_compressions)),
                    "std": float(np.std(word_compressions)),
                },
                "avg_latency_ms": float(np.mean(latencies)),
                "invalid_output_rate": invalid_count / len(records) if records else 0.0,
                "fallback_rate": fallback_count / len(records) if records else 0.0,
            }

        return results
