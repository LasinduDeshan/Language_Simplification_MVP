"""Feature matrix builder and transformation pipeline for Stage 22."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from app.complexity_analysis.feature_registry import (
    FEATURE_NAMES,
    CONTINUOUS_FEATURE_NAMES,
    BINARY_FEATURE_NAMES,
    validate_feature_allowlist,
)


class FeatureBuilder:
    """Extracts, computes, and standardizes governed complexity features."""

    def __init__(self, scaler: Optional[StandardScaler] = None):
        self.scaler = scaler or StandardScaler()
        self.is_fitted = scaler is not None
        self.feature_names = list(FEATURE_NAMES)

    def extract_raw_features(self, record: Dict[str, Any]) -> Dict[str, float]:
        """Extracts and computes the exact governed features from a Stage 21 record."""
        feat = {}

        # 1. Surface features
        char_count = float(record.get("char_count", 0))
        token_count = float(record.get("token_count", 0))
        word_count = float(record.get("word_count", 0))
        sentence_count = max(1.0, float(record.get("sentence_count", 1)))
        punct_count = float(record.get("punct_count", 0))

        feat["char_count"] = char_count
        feat["token_count"] = token_count
        feat["word_count"] = word_count
        feat["sentence_count"] = sentence_count
        feat["punct_count"] = punct_count

        feat["avg_word_length"] = float(record.get("avg_word_length", (char_count / max(1.0, word_count))))
        feat["avg_sentence_length"] = float(record.get("avg_sentence_length", (token_count / sentence_count)))

        syllable_count = float(record.get("syllable_count", 0))
        feat["syllable_count"] = syllable_count
        feat["avg_syllables_per_word"] = syllable_count / max(1.0, word_count)

        long_word_count = float(record.get("long_word_count", 0))
        feat["long_word_count"] = long_word_count
        feat["long_word_ratio"] = long_word_count / max(1.0, word_count)
        feat["type_token_ratio"] = float(record.get("type_token_ratio", 0.0))

        # 2. Lexical & POS
        noun_count = float(record.get("noun_count", 0))
        verb_count = float(record.get("verb_count", 0))
        adj_count = float(record.get("adj_count", 0))
        adv_count = float(record.get("adv_count", 0))

        feat["noun_count"] = noun_count
        feat["noun_ratio"] = noun_count / max(1.0, word_count)
        feat["verb_count"] = verb_count
        feat["verb_ratio"] = verb_count / max(1.0, word_count)
        feat["adj_count"] = adj_count
        feat["adj_ratio"] = adj_count / max(1.0, word_count)
        feat["adv_count"] = adv_count
        feat["adv_ratio"] = adv_count / max(1.0, word_count)

        content_words = noun_count + verb_count + adj_count + adv_count
        feat["content_word_ratio"] = content_words / max(1.0, word_count)
        feat["function_word_ratio"] = max(0.0, 1.0 - feat["content_word_ratio"])

        # 3. Syntactic
        feat["max_dependency_depth"] = float(record.get("max_dependency_depth", 0))
        feat["avg_dependency_depth"] = float(record.get("avg_dependency_depth", 0.0))
        feat["clause_count"] = float(record.get("clause_count", 0))

        passive = record.get("passive_voice", False)
        if isinstance(passive, str):
            passive = passive.lower() in ("true", "1", "yes")
        feat["passive_voice"] = 1.0 if passive else 0.0

        # 4. Semantic load
        feat["negation_count"] = float(record.get("negation_count", 0))
        feat["quantity_count"] = float(record.get("quantity_count", 0))

        return feat

    def build_feature_dataframe(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts a list of records into a validated DataFrame adhering to the allowlist."""
        rows = []
        for r in records:
            rows.append(self.extract_raw_features(r))
        df = pd.DataFrame(rows, columns=self.feature_names)
        df = df.fillna(0.0)

        # Validate allowlist
        valid, violations = validate_feature_allowlist(list(df.columns))
        if not valid:
            raise ValueError(f"Feature allowlist validation failed: {violations}")

        return df

    def fit(self, records: List[Dict[str, Any]]) -> "FeatureBuilder":
        """Fits the continuous feature scaler on the provided records (training split only)."""
        df = self.build_feature_dataframe(records)
        continuous_data = df[CONTINUOUS_FEATURE_NAMES].values
        self.scaler.fit(continuous_data)
        self.is_fitted = True
        return self

    def transform(self, records: List[Dict[str, Any]]) -> np.ndarray:
        """Transforms records into a standardized numerical feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("FeatureBuilder must be fitted on training data before calling transform.")

        df = self.build_feature_dataframe(records)
        scaled_cont = self.scaler.transform(df[CONTINUOUS_FEATURE_NAMES].values)
        binary_data = df[BINARY_FEATURE_NAMES].values

        # Combine continuous + binary features in declared order
        combined_matrix = np.zeros((len(df), len(self.feature_names)), dtype=np.float64)
        cont_idx = [self.feature_names.index(c) for c in CONTINUOUS_FEATURE_NAMES]
        bin_idx = [self.feature_names.index(b) for b in BINARY_FEATURE_NAMES]

        combined_matrix[:, cont_idx] = scaled_cont
        combined_matrix[:, bin_idx] = binary_data

        return combined_matrix

    def fit_transform(self, records: List[Dict[str, Any]]) -> np.ndarray:
        """Fits on records and returns the transformed matrix."""
        self.fit(records)
        return self.transform(records)
