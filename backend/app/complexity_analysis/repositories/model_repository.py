"""Repository for saving and loading Stage 22 model and preprocessor packages."""

from pathlib import Path
from typing import Any, Dict, Optional
import joblib


class ModelRepository:
    """Serializes and deserializes trained model components, preprocessors, and OOD detectors."""

    def __init__(self, models_dir: Path = Path("data/complexity_analysis/en/source-0.2.0/preprocessing-1.0.0/classifier-1.0.0/models")):
        self.models_dir = models_dir

    def save_package(
        self,
        classifier: Any,
        feature_builder: Any,
        calibrator: Any,
        ood_detector: Any,
    ) -> Dict[str, Path]:
        """Saves all 4 model package components to disk."""
        self.models_dir.mkdir(parents=True, exist_ok=True)

        paths = {
            "selected_model": self.models_dir / "selected_model.joblib",
            "preprocessing_transformer": self.models_dir / "preprocessing_transformer.joblib",
            "calibration_model": self.models_dir / "calibration_model.joblib",
            "ood_detector": self.models_dir / "ood_detector.joblib",
        }

        joblib.dump(classifier, paths["selected_model"])
        joblib.dump(feature_builder, paths["preprocessing_transformer"])
        joblib.dump(calibrator, paths["calibration_model"])
        joblib.dump(ood_detector, paths["ood_detector"])

        return paths

    def load_package(self) -> Dict[str, Any]:
        """Loads all 4 model package components from disk."""
        paths = {
            "selected_model": self.models_dir / "selected_model.joblib",
            "preprocessing_transformer": self.models_dir / "preprocessing_transformer.joblib",
            "calibration_model": self.models_dir / "calibration_model.joblib",
            "ood_detector": self.models_dir / "ood_detector.joblib",
        }

        for name, p in paths.items():
            if not p.exists():
                raise FileNotFoundError(f"Model package artifact '{name}' not found at {p}")

        return {
            "classifier": joblib.load(paths["selected_model"]),
            "feature_builder": joblib.load(paths["preprocessing_transformer"]),
            "calibrator": joblib.load(paths["calibration_model"]),
            "ood_detector": joblib.load(paths["ood_detector"]),
        }
