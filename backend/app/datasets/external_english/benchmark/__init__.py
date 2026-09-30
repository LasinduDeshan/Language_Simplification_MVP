"""Benchmark evaluation package for external English simplification datasets."""

from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_complexity_reduction,
    compute_sari,
    compute_semantic_similarity_proxy,
)
from app.datasets.external_english.benchmark.runner import ASSETBenchmarkRunner
from app.datasets.external_english.benchmark.simplifiers import (
    DeterministicFallbackSimplifier,
    GeminiLLMSimplifier,
    IdentitySimplifier,
    RuleBasedSimplifier,
)

__all__ = [
    "compute_sari",
    "compute_bleu",
    "compute_semantic_similarity_proxy",
    "compute_complexity_reduction",
    "IdentitySimplifier",
    "RuleBasedSimplifier",
    "DeterministicFallbackSimplifier",
    "GeminiLLMSimplifier",
    "ASSETBenchmarkRunner",
]
