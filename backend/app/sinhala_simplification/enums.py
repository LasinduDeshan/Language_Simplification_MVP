"""
Stage 33 — Governed Enums for Sinhala Linguistic Simplification and Rewrite Engine.
"""

from enum import Enum


class RuleType(str, Enum):
    """Permitted Stage 33 rule types."""
    LEXICAL_SUBSTITUTION = "LEXICAL_SUBSTITUTION"
    PHRASE_SUBSTITUTION = "PHRASE_SUBSTITUTION"
    SENTENCE_SPLIT = "SENTENCE_SPLIT"
    CONSERVATIVE_SYNTACTIC = "CONSERVATIVE_SYNTACTIC"
    FALLBACK_UNCHANGED = "FALLBACK_UNCHANGED"


class RuleStatus(str, Enum):
    """Rule lifecycle status."""
    TECHNICAL_DRAFT = "TECHNICAL_DRAFT"
    FROZEN_FOR_TEST = "FROZEN_FOR_TEST"
    REJECTED = "REJECTED"


class AuthoringMethod(str, Enum):
    """Method used to author the rule."""
    TECHNICAL_RULE_AUTHORING = "technical_rule_authoring"


class RuleAttemptTerminalStatus(str, Enum):
    """Mutually exclusive terminal status for an evaluated rule attempt."""
    NOT_APPLICABLE = "NOT_APPLICABLE"
    CANDIDATE_GENERATED = "CANDIDATE_GENERATED"
    DEFERRED_BEFORE_GENERATION = "DEFERRED_BEFORE_GENERATION"
    FAILED_INTERNAL = "FAILED_INTERNAL"


class CandidateTerminalStatus(str, Enum):
    """Mutually exclusive terminal status for a generated rewrite candidate."""
    SELECTED = "SELECTED"
    NOT_SELECTED_LOWER_RANK = "NOT_SELECTED_LOWER_RANK"
    BLOCKED_PROTECTED_SPAN = "BLOCKED_PROTECTED_SPAN"
    BLOCKED_MEANING_GUARD = "BLOCKED_MEANING_GUARD"
    DEFERRED_MANUAL_REVIEW = "DEFERRED_MANUAL_REVIEW"
    FAILED_INTERNAL = "FAILED_INTERNAL"


class OperationType(str, Enum):
    """Atomic transformation operation types."""
    REPLACE = "REPLACE"
    INSERT = "INSERT"
    DELETE = "DELETE"
    SPLIT = "SPLIT"


class MappingStatus(str, Enum):
    """Transformation mapping state and cardinality."""
    ONE_TO_ONE = "one_to_one"
    MANY_TO_ONE = "many_to_one"
    ONE_TO_MANY = "one_to_many"
    INSERTED = "inserted"
    DELETED = "deleted"
    NON_LOCAL = "non_local"
    UNMAPPED = "unmapped"


class ProtectedSpanCategory(str, Enum):
    """Meaning-critical protected span categories."""
    NAMED_ENTITY = "NAMED_ENTITY"
    NUMBER_NUMERIC = "NUMBER_NUMERIC"
    DATE_TIME = "DATE_TIME"
    UNIT_MEASUREMENT = "UNIT_MEASUREMENT"
    CURRENCY = "CURRENCY"
    NEGATION_MARKER = "NEGATION_MARKER"
    MODALITY_CONDITION = "MODALITY_CONDITION"
    QUOTATION_DIRECT_SPEECH = "QUOTATION_DIRECT_SPEECH"
    IDENTIFIER_CODE_URL = "IDENTIFIER_CODE_URL"
    PARENTHETICAL_REFERENCE = "PARENTHETICAL_REFERENCE"
    MIXED_SCRIPT_TERM = "MIXED_SCRIPT_TERM"
    STAGE32_REVIEW_REQUIRED_VOCABULARY = "STAGE32_REVIEW_REQUIRED_VOCABULARY"


class GuardType(str, Enum):
    """Mandatory semantic and structural preservation guards."""
    ENTITY_PRESERVATION = "ENTITY_PRESERVATION"
    NUMBER_PRESERVATION = "NUMBER_PRESERVATION"
    DATE_TIME_PRESERVATION = "DATE_TIME_PRESERVATION"
    UNIT_PRESERVATION = "UNIT_PRESERVATION"
    NEGATION_PRESERVATION = "NEGATION_PRESERVATION"
    MODALITY_PRESERVATION = "MODALITY_PRESERVATION"
    QUOTATION_PRESERVATION = "QUOTATION_PRESERVATION"
    GRAPHEME_CLUSTER_INTEGRITY = "GRAPHEME_CLUSTER_INTEGRITY"
    UNICODE_REPLACEMENT_CHAR_CHECK = "UNICODE_REPLACEMENT_CHAR_CHECK"
    MEANING_CRITICAL_SCOPE_CHECK = "MEANING_CRITICAL_SCOPE_CHECK"


class FinalDisposition(str, Enum):
    """Authoritative terminal disposition for a simplification request."""
    DRAFT_REWRITE_SELECTED = "DRAFT_REWRITE_SELECTED"
    UNCHANGED_NO_APPLICABLE_RULE = "UNCHANGED_NO_APPLICABLE_RULE"
    UNCHANGED_ALL_CANDIDATES_BLOCKED = "UNCHANGED_ALL_CANDIDATES_BLOCKED"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    REJECTED_SOURCE_INELIGIBLE = "REJECTED_SOURCE_INELIGIBLE"
    REJECTED_INVALID_PREPROCESSING_STATE = "REJECTED_INVALID_PREPROCESSING_STATE"
    FAILED_INTERNAL_ERROR = "FAILED_INTERNAL_ERROR"


class Partition(str, Enum):
    """Dataset partition isolation boundary."""
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class CorpusView(str, Enum):
    """Governed corpus views."""
    CANONICAL_ANALYTICAL_150 = "canonical_analytical_150"
    PILOT_PROVENANCE_180 = "pilot_provenance_180"
