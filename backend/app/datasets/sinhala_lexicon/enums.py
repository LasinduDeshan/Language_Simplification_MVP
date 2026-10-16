"""
Enums for Stage 32 Sinhala Child-Vocabulary Lexicon Construction.
Enforces strict separation between occurrence-level dispositions,
entry-level terminal dispositions, provisional technical bands,
and expert review decisions.
"""

from enum import Enum

class OccurrenceDisposition(str, Enum):
    """Occurrence-level terminal dispositions with left-to-right evaluation precedence."""
    REJECTED_PRIVACY_OR_SECURITY = "REJECTED_PRIVACY_OR_SECURITY"
    REJECTED_INVALID_SOURCE_EVIDENCE = "REJECTED_INVALID_SOURCE_EVIDENCE"
    EXCLUDED_TOKEN_CLASS = "EXCLUDED_TOKEN_CLASS"
    MANUAL_REVIEW_OCCURRENCE = "MANUAL_REVIEW_OCCURRENCE"
    INCLUDED_CANDIDATE_OCCURRENCE = "INCLUDED_CANDIDATE_OCCURRENCE"

class TerminalEntryDisposition(str, Enum):
    """Candidate entry terminal dispositions with left-to-right first-matching precedence."""
    REJECTED_PRIVACY_OR_SECURITY = "REJECTED_PRIVACY_OR_SECURITY"
    REJECTED_INVALID_SOURCE_EVIDENCE = "REJECTED_INVALID_SOURCE_EVIDENCE"
    EXCLUDED_NON_LEXICAL = "EXCLUDED_NON_LEXICAL"
    EXCLUDED_NON_SINHALA = "EXCLUDED_NON_SINHALA"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    ACCEPTED_DRAFT_LEXICON_ENTRY = "ACCEPTED_DRAFT_LEXICON_ENTRY"

class ProvisionalVocabularyBand(str, Enum):
    """Technical review workflow bands. Not validated child acquisition age."""
    FOUNDATIONAL_CANDIDATE = "FOUNDATIONAL_CANDIDATE"
    EARLY_CANDIDATE = "EARLY_CANDIDATE"
    DEVELOPING_CANDIDATE = "DEVELOPING_CANDIDATE"
    ADVANCED_CANDIDATE = "ADVANCED_CANDIDATE"
    SPECIALIZED_OR_PROPER_CANDIDATE = "SPECIALIZED_OR_PROPER_CANDIDATE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    EXCLUDED_NON_LEXICAL = "EXCLUDED_NON_LEXICAL"

class LemmaMethod(str, Enum):
    """Method provenance for candidate lemma hypotheses."""
    IDENTITY_CANONICAL = "identity_canonical"
    RULE_BASED_INFLECTION_V1 = "rule_based_inflection_v1"
    RULE_BASED_DERIVATION_V1 = "rule_based_derivation_v1"
    MANUAL_OVERRIDE = "manual_override"

class ReviewDecision(str, Enum):
    """Human review categorical decisions."""
    NOT_REVIEWED = "NOT_REVIEWED"
    ACCEPT = "ACCEPT"
    MODIFY = "MODIFY"
    REJECT = "REJECT"
    UNCERTAIN = "UNCERTAIN"

class AgeBandReviewDecision(str, Enum):
    """Human expert age band assignment decisions."""
    NOT_REVIEWED = "NOT_REVIEWED"
    FOUNDATIONAL = "FOUNDATIONAL"
    EARLY = "EARLY"
    DEVELOPING = "DEVELOPING"
    ADVANCED = "ADVANCED"
    NOT_CHILD_VOCABULARY = "NOT_CHILD_VOCABULARY"
    UNCERTAIN = "UNCERTAIN"

class FieldExportPolicy(str, Enum):
    """Granular field-level exposure policies."""
    PUBLIC_PERMITTED_STANDALONE = "PUBLIC_PERMITTED_STANDALONE"
    PUBLIC_PERMITTED_AGGREGATE = "PUBLIC_PERMITTED_AGGREGATE"
    RESTRICTED_PROTECTED_INTERNAL = "RESTRICTED_PROTECTED_INTERNAL"
    METADATA_ONLY = "METADATA_ONLY"
