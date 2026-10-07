"""
Standard enums for dataset governance, provenance, rights, and workflow status.
"""
from enum import Enum

class LanguageCode(str, Enum):
    EN = "en"
    SI = "si"  # Declared for multilingual schema readiness (no Sinhala data in Stage 14)

class ActivityOwner(str, Enum):
    COMPONENT_1 = "component_1"
    COMPONENT_2_AR = "component_2_ar"
    COMPONENT_3_LANGUAGE = "component_3_language"
    SHARED = "shared"

class PrimaryDomain(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    COMPREHENSION = "comprehension"
    INSTRUCTION_FOLLOWING = "instruction_following"

class SupportLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ValidationStatus(str, Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETIRED = "retired"

class SourceType(str, Enum):
    TEAM_AUTHORED = "team_authored"
    EXPERT_AUTHORED = "expert_authored"
    OPEN_LICENCE = "open_licence"
    PERMISSION_GRANTED = "permission_granted"
    GENERATED = "generated"
    INTERACTION_DERIVED = "interaction_derived"

class ConsentStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    NOT_VERIFIED = "not_verified"
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

class ResearchEligibilityStatus(str, Enum):
    NOT_ASSESSED = "not_assessed"
    INELIGIBLE = "ineligible"
    ELIGIBLE = "eligible"
    WITHDRAWN = "withdrawn"

class AdaptationPolicy(str, Enum):
    NONE = "none"
    PRESENTATION_ONLY = "presentation_only"
    INSTRUCTION_ONLY = "instruction_only"
    CONTROLLED = "controlled"

class ResponseMode(str, Enum):
    MANUAL = "manual"
    SPEECH = "speech"
    TOUCH = "touch"
    AR_INTERACTION = "ar_interaction"
    IMPORTED = "imported"

class Outcome(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    SKIPPED = "skipped"
    ADULT_SUPPORT_REQUIRED = "adult_support_required"
    IN_PROGRESS = "in_progress"

class MigrationStatus(str, Enum):
    MIGRATED = "migrated"
    EXCLUDED = "excluded"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class ContentType(str, Enum):
    INSTRUCTION = "instruction"
    STIMULUS_PROMPT = "stimulus_prompt"
    FEEDBACK_CUE = "feedback_cue"
    VOCABULARY_DEFINITION = "vocabulary_definition"
