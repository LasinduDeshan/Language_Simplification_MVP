"""Master ComplexityAnalysisPipeline orchestrating end-to-end difficulty classification."""

from typing import Any, Dict, List, Optional
import hashlib
import json
import uuid
import numpy as np

from app.complexity_analysis.schemas import (
    ComplexityClassificationResult,
    DifficultyLabel,
)
from app.complexity_analysis.feature_builder import FeatureBuilder
from app.complexity_analysis.models.base import BaseComplexityClassifier
from app.complexity_analysis.calibration import ProbabilityCalibrator
from app.complexity_analysis.ood_detector import OODDetector
from app.complexity_analysis.review_router import ReviewRouter
from app.complexity_analysis.explanation import ComplexityExplainer
from app.complexity_analysis.version import (
    STAGE22_CLASSIFIER_VERSION,
    STAGE22_FEATURE_SCHEMA_VERSION,
    STAGE22_PIPELINE_VERSION,
    STAGE22_PREPROCESSING_VERSION,
    STAGE22_SOURCE_DATASET_VERSION,
)


class ComplexityAnalysisPipeline:
    """End-to-end linguistic complexity classification and explainability pipeline."""

    CLASSES: List[DifficultyLabel] = ["easy", "medium", "hard"]

    def __init__(
        self,
        classifier: BaseComplexityClassifier,
        feature_builder: FeatureBuilder,
        calibrator: Optional[ProbabilityCalibrator] = None,
        ood_detector: Optional[OODDetector] = None,
        review_router: Optional[ReviewRouter] = None,
        explainer: Optional[ComplexityExplainer] = None,
    ):
        self.classifier = classifier
        self.feature_builder = feature_builder
        self.calibrator = calibrator or ProbabilityCalibrator()
        self.ood_detector = ood_detector or OODDetector()
        self.review_router = review_router or ReviewRouter()
        self.explainer = explainer or ComplexityExplainer()

    def classify_record(
        self,
        record: Dict[str, Any],
        text_role: Optional[str] = None,
        parser_failed: bool = False,
    ) -> ComplexityClassificationResult:
        """Classifies a single preprocessed record and produces an explainable result."""
        text_instance_id = record.get("text_instance_id", str(uuid.uuid4()))
        source_group_id = record.get("source_group_id") or record.get("parent_record_id")

        # 1. Feature extraction & scaling
        raw_features = self.feature_builder.extract_raw_features(record)
        X = self.feature_builder.transform([record])

        # 2. Raw model prediction & probability calibration
        uncalibrated_probs = self.classifier.predict_proba(X)
        if self.calibrator.is_fitted:
            calibrated_probs = self.calibrator.calibrate(uncalibrated_probs)[0]
        else:
            calibrated_probs = uncalibrated_probs[0]

        pred_idx = int(np.argmax(calibrated_probs))
        predicted_difficulty: DifficultyLabel = self.CLASSES[pred_idx]

        class_probabilities: Dict[DifficultyLabel, float] = {
            self.CLASSES[i]: float(round(calibrated_probs[i], 4)) for i in range(3)
        }

        # 3. OOD detection
        if self.ood_detector.is_fitted:
            ood_result = self.ood_detector.evaluate_instance(
                features=raw_features,
                text_role=text_role or record.get("text_role"),
                parser_failed=parser_failed or (record.get("processing_status") == "failed"),
            )
            is_ood = ood_result.is_out_of_distribution
            ood_violations = ood_result.violating_features
        else:
            is_ood = False
            ood_violations = []

        # 4. Review routing
        review_req, review_reasons, conf, margin = self.review_router.evaluate_routing(
            class_probabilities=class_probabilities,
            is_out_of_distribution=is_ood,
            ood_violations=ood_violations,
            parser_failed=parser_failed or (record.get("processing_status") == "failed"),
        )

        # 5. Explanations
        factors = self.explainer.generate_factors(
            features=raw_features,
            predicted_difficulty=predicted_difficulty,
        )

        # Record hash for auditability
        hash_payload = json.dumps(
            {
                "text_instance_id": text_instance_id,
                "predicted_difficulty": predicted_difficulty,
                "class_probabilities": class_probabilities,
                "confidence": conf,
            },
            sort_keys=True,
        )
        record_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

        return ComplexityClassificationResult(
            classification_id=f"CLS-{uuid.uuid4().hex[:12].upper()}",
            text_instance_id=text_instance_id,
            source_group_id=source_group_id,
            predicted_difficulty=predicted_difficulty,
            class_probabilities=class_probabilities,
            confidence=float(round(conf, 4)),
            confidence_threshold=self.review_router.confidence_threshold,
            margin=float(round(margin, 4)),
            margin_threshold=self.review_router.margin_threshold,
            review_required=review_req,
            review_reasons=review_reasons,
            is_out_of_distribution=is_ood,
            complexity_factors=factors,
            model_name=self.classifier.model_name,
            model_version=STAGE22_CLASSIFIER_VERSION,
            feature_schema_version=STAGE22_FEATURE_SCHEMA_VERSION,
            preprocessing_pipeline_version=STAGE22_PREPROCESSING_VERSION,
            source_dataset_version=STAGE22_SOURCE_DATASET_VERSION,
            record_hash=record_hash,
        )

    def classify_batch(
        self,
        records: List[Dict[str, Any]],
    ) -> List[ComplexityClassificationResult]:
        """Classifies a batch of preprocessed records."""
        return [self.classify_record(r) for r in records]
