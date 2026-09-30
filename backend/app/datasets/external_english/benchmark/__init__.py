"""Benchmark evaluation package for external English simplification datasets."""

from app.datasets.external_english.benchmark.metrics import (
    compute_bleu,
    compute_bertscore_proxy,
    compute_complexity_reduction,
    compute_sari,
)
from app.datasets.external_english.benchmark.runner import ASSETBenchmarkRunner
from app.datasets.external_english.benchmark.simplifiers import (
    GenericLLMSimplifier,
    IdentitySimplifier,
    RuleBasedSimplifier,
)

__all__ = [
    "compute_sari",
    "compute_bleu",
    "compute_bertscore_proxy",
    "compute_complexity_reduction",
    "IdentitySimplifier",
    "RuleBasedSimplifier",
    "GenericLLMSimplifier",
    "ASSETBenchmarkRunner",
]
