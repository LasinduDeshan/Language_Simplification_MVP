"""Deterministic Out-of-Distribution (OOD) Detector for Stage 22."""

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from app.complexity_analysis.schemas import OODDetectionResult
from app.complexity_analysis.feature_registry import (
    CONTINUOUS_FEATURE_NAMES,
    BINARY_FEATURE_NAMES,
)


class OODDetector:
    """Deterministic quantile-based OOD detector enforcing [Q0.01, Q0.99] bounds on continuous features."""

    def __init__(
        self,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
        max_allowed_violations: int = 2,
    ):
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.max_allowed_violations = max_allowed_violations
        self.feature_bounds: Dict[str, Tuple[float, float]] = {}
        self.valid_text_roles: Set[str] = set()
        self.constant_features: Set[str] = set()
        self.is_fitted = False

    def fit(self, df_train: pd.DataFrame, text_roles: Optional[List[str]] = None) -> "OODDetector":
        """Fits empirical quantile bounds on training continuous features and records valid text roles."""
        self.feature_bounds.clear()
        self.constant_features.clear()

        # Learn bounds for continuous features
        for feat in CONTINUOUS_FEATURE_NAMES:
            if feat not in df_train.columns:
                continue

            series = df_train[feat].astype(float)
            q_low = float(series.quantile(self.lower_quantile))
            q_high = float(series.quantile(self.upper_quantile))

            # If feature is constant in training, exclude from range scoring
            if q_low == q_high:
                self.constant_features.add(feat)
            else:
                self.feature_bounds[feat] = (q_low, q_high)

        # Record valid text roles
        if text_roles:
            self.valid_text_roles = set(text_roles)
        elif "text_role" in df_train.columns:
            self.valid_text_roles = set(df_train["text_role"].dropna().unique())
        else:
            self.valid_text_roles = {"source_text", "simplified_text", "activity_instruction", "activity_prompt", "lexicon_definition", "lexicon_example"}

        self.is_fitted = True
        return self

    def evaluate_instance(
        self,
        features: Dict[str, Any],
        text_role: Optional[str] = None,
        parser_failed: bool = False,
    ) -> OODDetectionResult:
        """Evaluates a single instance against fitted bounds and returns an OODDetectionResult."""
        if not self.is_fitted:
            raise RuntimeError("OODDetector must be fitted before evaluating instances.")

        if parser_failed:
            return OODDetectionResult(
                is_out_of_distribution=True,
                anomaly_score=10.0,
                violating_features=["parser_failure"],
                violation_details={"parser_failure": {"status": 1.0}},
            )

        violating_features: List[str] = []
        violation_details: Dict[str, Dict[str, float]] = {}

        # 1. Categorical / text-role check
        if text_role and text_role not in self.valid_text_roles:
            violating_features.append(f"unseen_text_role:{text_role}")
            violation_details[f"unseen_text_role:{text_role}"] = {"observed": -1.0, "valid": 0.0}

        # 2. Binary features domain check
        for feat in BINARY_FEATURE_NAMES:
            if feat in features:
                val = float(features[feat])
                if val not in (0.0, 1.0):
                    violating_features.append(feat)
                    violation_details[feat] = {"observed": val, "expected_binary": 1.0}

        # 3. Continuous feature bounds check
        for feat, (q_low, q_high) in self.feature_bounds.items():
            if feat in features:
                val = float(features[feat])
                if val < q_low or val > q_high:
                    violating_features.append(feat)
                    violation_details[feat] = {
                        "observed": val,
                        "lower_bound": q_low,
                        "upper_bound": q_high,
                    }

        anomaly_score = float(len(violating_features))
        is_ood = anomaly_score >= self.max_allowed_violations or len(violating_features) > 0 and any("unseen_text_role" in v for v in violating_features)

        return OODDetectionResult(
            is_out_of_distribution=is_ood,
            anomaly_score=anomaly_score,
            violating_features=violating_features,
            violation_details=violation_details,
        )
