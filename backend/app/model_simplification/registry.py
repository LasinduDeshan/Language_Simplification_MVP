"""
Stage 26 Model Registry.
Tracks candidate models, checkpoint revisions, licences, weight hashes, and execution configurations.
"""
import csv
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    model_id: str
    provider: str  # google, huggingface, local_rule
    repo_or_endpoint: str
    commit_revision: Optional[str] = None
    tokenizer_revision: Optional[str] = None
    licence: str
    intended_mode: str  # pretrained_zero_shot, pretrained_prefix_prompt, fine_tuned_internal_pilot, deterministic_stage25, hybrid
    device_type: str = "cpu"
    datatype: str = "float32"
    decoding_strategy: str = "beam_search"
    num_beams: int = 4
    max_input_length: int = 256
    max_output_length: int = 128
    temperature: float = 0.2
    config_hash: Optional[str] = None

    def compute_config_hash(self) -> str:
        s = f"{self.model_id}:{self.provider}:{self.repo_or_endpoint}:{self.commit_revision}:{self.licence}:{self.intended_mode}:{self.decoding_strategy}:{self.num_beams}"
        return hashlib.sha256(s.encode("utf-8")).hexdigest()


class ModelRegistry:
    """
    Central registry for Stage 26 candidate models and adapters.
    """

    def __init__(self):
        self._models: Dict[str, ModelMetadata] = {}
        self._load_default_registry()

    def _load_default_registry(self):
        # 1. Gemini 1.5 Flash (Prompted)
        gemini = ModelMetadata(
            model_id="gemini-1.5-flash-prompted",
            provider="google",
            repo_or_endpoint="gemini-1.5-flash",
            licence="Google AI Terms of Service",
            intended_mode="pretrained_prefix_prompt",
            temperature=0.2,
            decoding_strategy="greedy_sampling",
        )
        gemini.config_hash = gemini.compute_config_hash()
        self.register(gemini)

        # 2. mT5 Base (Zero-Shot / Instruction Prefix)
        mt5 = ModelMetadata(
            model_id="mt5-base-zero-shot",
            provider="huggingface",
            repo_or_endpoint="google/mt5-base",
            commit_revision="aa72111",
            tokenizer_revision="aa72111",
            licence="Apache-2.0",
            intended_mode="pretrained_zero_shot",
            num_beams=4,
        )
        mt5.config_hash = mt5.compute_config_hash()
        self.register(mt5)

        # 3. mBART-50 (Zero-Shot / Prefix)
        mbart = ModelMetadata(
            model_id="mbart-large-50-zero-shot",
            provider="huggingface",
            repo_or_endpoint="facebook/mbart-large-50-many-to-many-mmt",
            commit_revision="61869e5",
            tokenizer_revision="61869e5",
            licence="MIT",
            intended_mode="pretrained_zero_shot",
            num_beams=4,
        )
        mbart.config_hash = mbart.compute_config_hash()
        self.register(mbart)

        # 4. Stage 25 Deterministic Controlled Engine (Comparator / Fallback)
        stage25 = ModelMetadata(
            model_id="stage25-controlled-deterministic",
            provider="local_rule",
            repo_or_endpoint="stage-25-complete-v2",
            commit_revision="6b785502b860d4e93d2d31b86bd653c33a210ac9",
            licence="project-internal",
            intended_mode="deterministic_stage25",
            decoding_strategy="deterministic_rules",
        )
        stage25.config_hash = stage25.compute_config_hash()
        self.register(stage25)

        # 5. Hybrid Generative + Stage 25 Validator
        hybrid = ModelMetadata(
            model_id="hybrid-gemini-stage25-validated",
            provider="hybrid",
            repo_or_endpoint="gemini-1.5-flash + stage25-rules",
            licence="project-internal",
            intended_mode="hybrid",
            decoding_strategy="generative_plus_surface_repair",
        )
        hybrid.config_hash = hybrid.compute_config_hash()
        self.register(hybrid)

    def register(self, model: ModelMetadata):
        if not model.config_hash:
            model.config_hash = model.compute_config_hash()
        self._models[model.model_id] = model

    def get(self, model_id: str) -> Optional[ModelMetadata]:
        return self._models.get(model_id)

    def list_models(self) -> List[ModelMetadata]:
        return list(self._models.values())

    def export_csv(self, out_path: Path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "model_id",
            "provider",
            "repo_or_endpoint",
            "commit_revision",
            "tokenizer_revision",
            "licence",
            "intended_mode",
            "device_type",
            "datatype",
            "decoding_strategy",
            "num_beams",
            "config_hash",
        ]
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for m in self._models.values():
                row = m.model_dump()
                filtered = {k: row.get(k) for k in fieldnames}
                writer.writerow(filtered)
