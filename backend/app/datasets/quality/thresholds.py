"""Configurable, versioned threshold constants and policies for Stage 15 Quality Validation."""

# Rule-set SemVer
QUALITY_RULE_SET_VERSION = "1.0.0"

# Overall Quality Score cutoffs
SCORE_PASS_MINIMUM = 85.0
SCORE_REVIEW_MINIMUM = 70.0

# Dimension Weights for Simplification Corpus
CORPUS_DIMENSION_WEIGHTS = {
    "meaning_preservation": 0.30,
    "grammar_fluency": 0.20,
    "simplicity_improvement": 0.20,
    "age_appropriateness": 0.15,
    "safety_answer_boundary": 0.15,
}

# Linguistic thresholds for English children aged 4-8
MAX_RECOMMENDED_ASL_TOKENS = 15
MAX_ALLOWABLE_ASL_TOKENS = 22

# Compression ratio thresholds (len(simplified) / len(original))
COMPRESSION_RATIO_MIN_WARN = 0.30
COMPRESSION_RATIO_MAX_WARN = 1.20
COMPRESSION_RATIO_MIN_ERR = 0.15
COMPRESSION_RATIO_MAX_ERR = 1.50

# Maximum syllables per word before flagged as complex for age 4-8
MAX_SYLLABLES_SIMPLE = 3
