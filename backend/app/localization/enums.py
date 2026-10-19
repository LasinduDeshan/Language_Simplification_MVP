"""
Stage 29 localization enums.
"""
from enum import Enum

class SupportedLanguage(str, Enum):
    EN = "en"
    SI = "si"

class SupportedLocale(str, Enum):
    EN_LK = "en-LK"
    SI_LK = "si-LK"

class ScriptCode(str, Enum):
    LATN = "Latn"
    SINH = "Sinh"

class TextDirection(str, Enum):
    LTR = "ltr"
    RTL = "rtl"

class FieldCategory(str, Enum):
    EDUCATIONAL_TEXT = "educational_text"
    TECHNICAL_FIXTURE = "technical_fixture"
    IDENTIFIER = "identifier"
    USERNAME = "username"
    LOG = "log"
    NLP_INPUT = "nlp_input"


class TargetDisclosureClass(str, Enum):
    INFERRED_ANSWER = "INFERRED_ANSWER"
    EXPLICIT_TASK_TARGET = "EXPLICIT_TASK_TARGET"


class TargetDisclosurePolicy(str, Enum):
    DO_NOT_REVEAL = "DO_NOT_REVEAL"
    MAY_REPEAT_TASK_TARGET = "MAY_REPEAT_TASK_TARGET"


class ContentLanguageStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class GovernedTaskType(str, Enum):
    VOCABULARY_NAMING = "VOCABULARY_NAMING"
    WORD_ORDERING = "WORD_ORDERING"
    SUBJECT_PREDICATE_IDENTIFICATION = "SUBJECT_PREDICATE_IDENTIFICATION"


TaskType = GovernedTaskType

