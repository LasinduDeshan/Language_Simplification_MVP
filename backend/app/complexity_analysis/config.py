"""Configuration and hyperparameter settings for Stage 22 Complexity Analysis."""

from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class ComplexityConfig(BaseModel):
    """Immutable runtime and training configuration for Stage 22."""

    model_config = ConfigDict(extra="forbid")

    confidence_threshold: float = Field(default=0.80, ge=0.5, le=1.0)
    margin_threshold: float = Field(default=0.15, ge=0.0, le=1.0)
    min_folds_source_groups: int = Field(default=3, ge=2)
    calibration_method: Literal["isotonic", "sigmoid"] = "isotonic"
    ood_lower_quantile: float = Field(default=0.01, ge=0.0, le=0.1)
    ood_upper_quantile: float = Field(default=0.99, ge=0.9, le=1.0)
    hard_to_easy_safety_target: float = Field(default=0.02, ge=0.0, le=0.1)
    random_state: int = 42

    # Paths
    base_data_dir: Path = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0")
    stage21_features_dir: Path = Path("data/preprocessed_features/en/source-0.2.0/pipeline-1.0.0")
