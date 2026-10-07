"""Benchmark runner executing baseline models on ASSET dataset with clear provider attribution."""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_complexity_reduction,
    compute_sari,
    compute_semantic_similarity_proxy,
)
from app.datasets.external_english.benchmark.simplifiers import (
    DeterministicFallbackSimplifier,
    GeminiLLMSimplifier,
    IdentitySimplifier,
    RuleBasedSimplifier,
)
from app.datasets.external_english.schemas import NormalizedExternalRecord


class ASSETBenchmarkRunner:
    """Orchestrates benchmark evaluation of multiple simplification baselines on ASSET."""

    def __init__(self):
        self.active_simplifiers = {
            "identity_baseline": IdentitySimplifier(),
            "rule_based_simplifier": RuleBasedSimplifier(),
            "deterministic_fallback": DeterministicFallbackSimplifier(),
        }
        self.gemini_provider = GeminiLLMSimplifier()

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
            "provider_status": {
                "gemini": self.gemini_provider.get_evaluation_status(),
            },
        }

        # 1. Evaluate Active Offline Baselines
        for name, simplifier in self.active_simplifiers.items():
            sari_scores = []
            add_scores = []
            keep_scores = []
            del_scores = []
            bleu_scores = []
            semantic_proxies = []
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
                sem_proxy = compute_semantic_similarity_proxy(pred, refs)
                comp = compute_complexity_reduction(src, pred)

                sari_scores.append(sari)
                add_scores.append(add_s)
                keep_scores.append(keep_s)
                del_scores.append(del_s)
                bleu_scores.append(bleu)
                semantic_proxies.append(sem_proxy)
                fkgl_reductions.append(comp["fkgl_reduction"])
                word_compressions.append(comp["word_compression_ratio"])

            results["baselines"][name] = {
                "evaluated_outputs": len(records) - invalid_count,
                "evaluation_status": "Valid",
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
                "semantic_similarity_proxy": {
                    "mean": float(np.mean(semantic_proxies)),
                    "std": float(np.std(semantic_proxies)),
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

        # 2. Record Un-Evaluated / Offline Providers Explicitly
        if not self.gemini_provider.is_available():
            results["baselines"]["gemini_llm"] = {
                "evaluated_outputs": 0,
                "evaluation_status": "Not evaluated—API unavailable/offline",
                "requested_provider": "gemini",
                "provider_calls_attempted": 0,
                "provider_outputs_received": 0,
                "fallback_outputs_generated": len(records),
                "provider_evaluation_status": "not_evaluated_offline",
                "metrics_attributed_to": "deterministic_fallback",
                "sari": None,
                "bleu": None,
                "semantic_similarity_proxy": None,
                "fkgl_reduction": None,
                "avg_latency_ms": None,
            }

        return results
