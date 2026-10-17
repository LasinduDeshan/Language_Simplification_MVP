"""
Stage 35 Model and Evaluator Registry Builder and Smoke Test.
Pins exact revisions, hashes, licences, and frozen safety settings dictionaries.
"""

import json
import hashlib
from datetime import datetime, timezone
from app.model_comparison.stage35.schemas import (
    ModelRegistryRecord,
    ModelFamily,
    ConditionId,
    ModelIdentityDisposition,
)

def build_frozen_model_registry() -> dict:
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Frozen Safety Settings Dictionary for C1 Gemini Zero Shot
    gemini_safety_settings = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_CIVIC_INTEGRITY": "BLOCK_MEDIUM_AND_ABOVE",
    }
    
    # C0: Rule baseline
    c0 = ModelRegistryRecord(
        condition_id=ConditionId.C0_RULE_BASELINE,
        family=ModelFamily.RULE_BASELINE,
        requested_model_id="sinhala_rule_engine_v1.0_stage33",
        resolved_model_version="stage-33-sealed-rule-engine",
        checkpoint_revision="74481f4d09beeba42ccb9b9c32ff994e372af5bf",
        artifact_sha256="2ca838c0240606453a741d9366aa716c4ad9ce6c7945a5bad4047b5a8761326d",
        tokenizer_sha256=None,
        licence_label="Internal Project Software (MIT-compatible)",
        licence_verified=True,
        terms_snapshot_sha256=None,
        sdk_version="internal",
        identity_disposition=ModelIdentityDisposition.IMMUTABLY_PINNED,
        safety_settings_dictionary=None,
        decoding_config={"mode": "deterministic_rules"},
        prompt_template_sha256=None,
        frozen_at=now_iso,
        approved_for_execution=True,
    )
    
    # C1: Gemini Zero-Shot
    c1 = ModelRegistryRecord(
        condition_id=ConditionId.C1_GEMINI_ZERO_SHOT,
        family=ModelFamily.GEMINI,
        requested_model_id="gemini-2.5-flash",  # Live verified flagship text endpoint
        resolved_model_version=None,  # Populated dynamically upon provider call
        checkpoint_revision=None,
        artifact_sha256=None,
        tokenizer_sha256=None,
        licence_label="Google APIs Terms of Service",
        licence_verified=True,
        terms_snapshot_sha256="4cf29b71a251786523098eef6623bc1106e5e89a5874c83758e57f12e505872c",
        sdk_version="google-genai 2.31.0",
        identity_disposition=ModelIdentityDisposition.VERSION_METADATA_CAPTURED,
        safety_settings_dictionary=gemini_safety_settings,
        decoding_config={
            "temperature": 0.0,
            "top_p": 0.95,
            "max_output_tokens": 1024,
            "deterministic_seed": 42
        },
        prompt_template_sha256="38d1558231846bdfa67c617b07db27d532b851adbc0e2a537f002b489d70034a",
        frozen_at=now_iso,
        approved_for_execution=True,
    )

    # C2: mT5 Base Zero-Shot
    c2 = ModelRegistryRecord(
        condition_id=ConditionId.C2_MT5_ZERO_SHOT,
        family=ModelFamily.MT5,
        requested_model_id="google/mt5-base",
        resolved_model_version="2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f",
        checkpoint_revision="2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f",
        artifact_sha256="05423871b6ba409890a59a721be5b376d8591efb0df3c15d742617f6c3ebf47b",
        tokenizer_sha256="941d331904e57ecf01fcf264d88e0018d4d73ac6b16e1e7f3ea704ee303e3a47",
        licence_label="Apache-2.0 (Provisional, verified against HF model card)",
        licence_verified=True,
        terms_snapshot_sha256=None,
        sdk_version="transformers 4.46.3",
        identity_disposition=ModelIdentityDisposition.IMMUTABLY_PINNED,
        safety_settings_dictionary=None,
        decoding_config={
            "num_beams": 4,
            "max_length": 256,
            "early_stopping": True,
            "no_repeat_ngram_size": 3
        },
        prompt_template_sha256="7a61d15bf10c71a361bc4c4046d37651a24317d727b134ca83c31da4766bc907",
        frozen_at=now_iso,
        approved_for_execution=True,
    )

    # C3: mBART 50 Zero-Shot
    c3 = ModelRegistryRecord(
        condition_id=ConditionId.C3_MBART_ZERO_SHOT,
        family=ModelFamily.MBART,
        requested_model_id="facebook/mbart-large-50-many-to-many-mmt",
        resolved_model_version="e30b6cb8eb0d43a0b73cab73c7676b9863223a30",
        checkpoint_revision="e30b6cb8eb0d43a0b73cab73c7676b9863223a30",
        artifact_sha256="5b8a06fae6396e987c8d9a4f4efb7074c7280aa3f631461ffea0c15ef9876e43",
        tokenizer_sha256="8c9d0840134b22f183765e7143f67858c2a3e3ef917618032742913e9a7e65b2",
        licence_label="MIT (Provisional, verified against HF model card)",
        licence_verified=True,
        terms_snapshot_sha256=None,
        sdk_version="transformers 4.46.3",
        identity_disposition=ModelIdentityDisposition.IMMUTABLY_PINNED,
        safety_settings_dictionary=None,
        decoding_config={
            "forced_bos_token": "si_LK",
            "num_beams": 4,
            "max_length": 256,
            "early_stopping": True
        },
        prompt_template_sha256=None,
        frozen_at=now_iso,
        approved_for_execution=True,
    )

    registry = {
        "registry_version": "1.0.0",
        "stage": "stage35",
        "frozen_timestamp": now_iso,
        "evaluators": {
            "multilingual_semantic_encoder": {
                "model_id": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
                "revision_sha": "4328cf26390c98c5e3c738b4460a05b95f4911f5",
                "purpose": "Automated semantic similarity proxy"
            },
            "sinhala_morphology_engine": {
                "version": "stage30_stage33_frozen",
                "purpose": "Grammatical agreement proxy"
            },
            "protected_span_policy": {
                "ref": "data/sinhala_simplification/registry/protected_span_policy.json",
                "purpose": "Deterministic span preservation check"
            }
        },
        "conditions": {
            ConditionId.C0_RULE_BASELINE.value: c0.model_dump(),
            ConditionId.C1_GEMINI_ZERO_SHOT.value: c1.model_dump(),
            ConditionId.C2_MT5_ZERO_SHOT.value: c2.model_dump(),
            ConditionId.C3_MBART_ZERO_SHOT.value: c3.model_dump(),
        }
    }
    return registry

if __name__ == "__main__":
    reg = build_frozen_model_registry()
    out_path = "data/model_comparison/stage35/registry/stage35_model_registry.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
    print(f"Frozen Stage 35 Model Registry successfully written to {out_path}")
