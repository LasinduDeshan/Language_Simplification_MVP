"""
Generates the explicit individual policy and configuration artifacts for Stage 35 freeze bundle.
"""

import json
from pathlib import Path

reg_dir = Path("data/model_comparison/stage35/registry")
reg_dir.mkdir(parents=True, exist_ok=True)

# 1. Prompt template
prompt_template = {
    "artifact_id": "S35-PROMPT-TEMPLATE-001",
    "language": "si",
    "locale": "si-LK",
    "script": "Sinh",
    "template": "Simplify the following Sinhala text for a young child while preserving meaning, named entities, numbers, and facts. Return only the simplified Sinhala text:\n\n{source_text}",
    "role": "PROMPT_TEMPLATE",
}
with open(reg_dir / "stage35_prompt_template.json", "w", encoding="utf-8") as f:
    json.dump(prompt_template, f, indent=2, ensure_ascii=False)

# 2. Decoding configuration
decoding_config = {
    "artifact_id": "S35-DECODING-CONFIG-001",
    "deterministic_mode": True,
    "gemini": {"temperature": 0.0, "top_p": 0.95, "max_output_tokens": 1024, "seed": 42},
    "mt5": {"num_beams": 4, "max_length": 256, "no_repeat_ngram_size": 3, "early_stopping": True},
    "mbart": {"forced_bos_token": "si_LK", "num_beams": 4, "max_length": 256, "early_stopping": True},
    "role": "DECODING_CONFIG",
}
with open(reg_dir / "stage35_decoding_config.json", "w", encoding="utf-8") as f:
    json.dump(decoding_config, f, indent=2, ensure_ascii=False)

# 3. Safety settings dictionary
safety_settings = {
    "artifact_id": "S35-SAFETY-SETTINGS-001",
    "provider": "google-genai",
    "thresholds": {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_CIVIC_INTEGRITY": "BLOCK_MEDIUM_AND_ABOVE",
    },
    "role": "SAFETY_SETTINGS",
}
with open(reg_dir / "stage35_safety_settings.json", "w", encoding="utf-8") as f:
    json.dump(safety_settings, f, indent=2, ensure_ascii=False)

# 4. Evaluator specification
evaluator_spec = {
    "artifact_id": "S35-EVALUATOR-SPEC-001",
    "multilingual_semantic_encoder": {
        "model_id": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        "revision_sha": "4328cf26390c98c5e3c738b4460a05b95f4911f5",
        "metric": "cosine_similarity",
    },
    "morphology_engine": {"version": "stage30_stage33_frozen"},
    "protected_span_policy": {"ref": "data/sinhala_simplification/registry/protected_span_policy.json"},
    "role": "EVALUATOR_SPEC",
}
with open(reg_dir / "stage35_evaluator_spec.json", "w", encoding="utf-8") as f:
    json.dump(evaluator_spec, f, indent=2, ensure_ascii=False)

# 5. Metric and gate specification
metrics_spec = {
    "artifact_id": "S35-METRICS-SPEC-001",
    "frozen_metric_count": 5,
    "metrics": [
        "source_char_len",
        "output_char_len",
        "compression_ratio",
        "semantic_similarity_proxy",
        "grammaticality_proxy",
    ],
    "critical_safety_gates": {
        "pipeline_introduced_u_fffd_max": 0,
        "protected_span_violation_max": 0,
        "valid_output_rate_min": 0.90,
    },
    "role": "METRICS_SPEC",
}
with open(reg_dir / "stage35_metrics_and_gates_spec.json", "w", encoding="utf-8") as f:
    json.dump(metrics_spec, f, indent=2, ensure_ascii=False)

# 6. Operational and retry policy
operational_policy = {
    "artifact_id": "S35-OPERATIONAL-POLICY-001",
    "random_seed": 42,
    "repetition_count_per_condition": 1,
    "max_retries": 3,
    "retry_backoff_base_sec": 2.0,
    "timeout_sec": 30.0,
    "role": "OPERATIONAL_POLICY",
}
with open(reg_dir / "stage35_operational_policy.json", "w", encoding="utf-8") as f:
    json.dump(operational_policy, f, indent=2, ensure_ascii=False)

# 7. Authorization and validation dryrun record
auth_record = {
    "artifact_id": "AUTH-S35-LOCKED-TEST-AUTHORIZED-RUN-001",
    "validation_run_id": "S35-VALI-DRYRUN-001",
    "validation_denominator": 13,
    "validation_status": "DRY_RUN_INFRASTRUCTURE_VALIDATION_PASSED",
    "authorized_by": "Technical Governance Lead",
    "authorized_at": "2026-10-17T07:51:52.172067+00:00",
    "first_locked_request_timestamp": "2026-10-17T08:03:24Z",
    "role": "AUTHORIZATION_RECORD",
}
with open(reg_dir / "stage35_authorization_record.json", "w", encoding="utf-8") as f:
    json.dump(auth_record, f, indent=2, ensure_ascii=False)

print("Generated all 7 detailed policy and specification artifacts.")
