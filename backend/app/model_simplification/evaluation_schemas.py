"""
Stage 26 Batch-Level Evaluation Schemas and DTOs.
Isolates corpus-wide metrics (SARI, SacreBLEU, FKGL delta) from runtime request/response structures.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ModelEvaluationResult(BaseModel):
    model_id: str
    provider: str
    model_mode: str  # pretrained_zero_shot, pretrained_prefix_prompt, fine_tuned_internal_pilot, deterministic_stage25, hybrid
    split: str  # validation, locked_test_full, locked_test_clean_subset, asset_benchmark
    total_samples: int
    # Simplification Quality Metrics
    sari_score: float
    sari_add: float
    sari_keep: float
    sari_del: float
    bleu_score: float
    fkgl_delta: float
    # Meaning & Safety Metrics
    exact_protected_recall: float
    meaning_preservation_rate: float
    # Final Outcome & Delivery Rates
    pass_rate: float
    repair_rate: float
    manual_review_rate: float
    rejection_rate: float
    fallback_rate: float
    # Operational & Reliability Metrics
    mean_latency_ms: float
    p95_latency_ms: float
    provider_calls_attempted: int
    provider_outputs_received: int
    timeout_rate: float
    retry_rate: float
    total_cost: float
    evaluated_at: str
