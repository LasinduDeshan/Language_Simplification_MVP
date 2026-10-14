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
