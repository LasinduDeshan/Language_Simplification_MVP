"""Repository for loading and filtering Stage 21 preprocessed linguistic feature records."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import json


class FeatureRepository:
    """Loads Stage 21 preprocessed linguistic feature records and metadata."""

    def __init__(self, base_dir: Path = Path("data/preprocessed_features/en/source-0.2.0/pipeline-1.0.0")):
        self.base_dir = base_dir
        self.features_csv_path = base_dir / "linguistic_features.csv"
        self.records_jsonl_path = base_dir / "preprocessed_records.jsonl"
        self.mappings_json_path = base_dir / "parent_to_text_mappings.json"

    def load_features_df(self) -> pd.DataFrame:
        """Loads the linguistic features CSV."""
        if not self.features_csv_path.exists():
            raise FileNotFoundError(f"Linguistic features CSV not found at {self.features_csv_path}")
        return pd.read_csv(self.features_csv_path)

    def load_features_records(self) -> List[Dict[str, Any]]:
        """Loads features as a list of dictionary records."""
        df = self.load_features_df()
        return df.to_dict(orient="records")

    def load_parent_mappings(self) -> Dict[str, Any]:
        """Loads parent to text instance mappings."""
        if not self.mappings_json_path.exists():
            return {}
        with open(self.mappings_json_path, "r", encoding="utf-8") as f:
            return json.load(f)
