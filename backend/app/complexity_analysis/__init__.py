"""Stage 22 English Complexity Analysis and Difficulty Classification module."""

from app.complexity_analysis.schemas import (
    ComplexityTrainingEligibility,
    ComplexityClassificationResult,
    ComplexityFactor,
    LabelAuditRecord,
    OODDetectionResult,
    ModelEvaluationSummary,
    DifficultyLabel,
)
from app.complexity_analysis.config import ComplexityConfig
from app.complexity_analysis.version import (
    STAGE22_PIPELINE_VERSION,
    STAGE22_CLASSIFIER_VERSION,
    STAGE22_FEATURE_SCHEMA_VERSION,
    STAGE22_SOURCE_DATASET_VERSION,
    STAGE22_PREPROCESSING_VERSION,
)
from app.complexity_analysis.eligibility import (
    determine_primary_disposition,
    evaluate_record_eligibility,
)
from app.complexity_analysis.label_auditor import LabelAuditor, LabelSufficiencyError
from app.complexity_analysis.feature_registry import (
    FEATURE_DEFINITIONS,
    FEATURE_NAMES,
    FEATURE_ALLOWLIST,
    CONTINUOUS_FEATURE_NAMES,
    BINARY_FEATURE_NAMES,
    validate_feature_allowlist,
    export_feature_dictionary,
)
from app.complexity_analysis.feature_builder import FeatureBuilder
from app.complexity_analysis.leakage_guard import LeakageGuard
from app.complexity_analysis.ood_detector import OODDetector
from app.complexity_analysis.review_router import ReviewRouter
from app.complexity_analysis.explanation import ComplexityExplainer
from app.complexity_analysis.calibration import (
    ProbabilityCalibrator,
    compute_expected_calibration_error,
)
from app.complexity_analysis.evaluator import (
    ModelEvaluator,
    compute_wilson_score_interval,
)
from app.complexity_analysis.pipeline import ComplexityAnalysisPipeline

__all__ = [
    "ComplexityTrainingEligibility",
    "ComplexityClassificationResult",
    "ComplexityFactor",
    "LabelAuditRecord",
    "OODDetectionResult",
    "ModelEvaluationSummary",
    "DifficultyLabel",
    "ComplexityConfig",
    "STAGE22_PIPELINE_VERSION",
    "STAGE22_CLASSIFIER_VERSION",
    "STAGE22_FEATURE_SCHEMA_VERSION",
    "STAGE22_SOURCE_DATASET_VERSION",
    "STAGE22_PREPROCESSING_VERSION",
    "determine_primary_disposition",
    "evaluate_record_eligibility",
    "LabelAuditor",
    "LabelSufficiencyError",
    "FEATURE_DEFINITIONS",
    "FEATURE_NAMES",
    "FEATURE_ALLOWLIST",
    "CONTINUOUS_FEATURE_NAMES",
    "BINARY_FEATURE_NAMES",
    "validate_feature_allowlist",
    "export_feature_dictionary",
    "FeatureBuilder",
    "LeakageGuard",
    "OODDetector",
    "ReviewRouter",
    "ComplexityExplainer",
    "ProbabilityCalibrator",
    "compute_expected_calibration_error",
    "ModelEvaluator",
    "compute_wilson_score_interval",
    "ComplexityAnalysisPipeline",
]
