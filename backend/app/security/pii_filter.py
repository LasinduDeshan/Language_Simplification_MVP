import re
from typing import Dict, Any

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")

def scrub_pii(text: str) -> str:
    """
    Scrubs accidental personal identifiable information (emails, phone numbers).
    """
    if not text:
        return ""
    scrubbed = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    scrubbed = PHONE_REGEX.sub("[REDACTED_PHONE]", scrubbed)
    return scrubbed

def prepare_llm_pseudonymous_context(
    learner_code: str,
    age: int,
    english_level: str,
    support_level: str,
    attempt_number: int,
    learning_objective: str,
    original_instruction: str,
    required_strategy: str,
    difficult_words: list,
    protected_answers: list
) -> Dict[str, Any]:
    """
    Builds strictly pseudonymous and minimal payload for LLM prompts.
    Never passes real names, schools, or complete history.
    """
    return {
        "age": age,
        "english_level": english_level,
        "support_level": support_level,
        "attempt_number": attempt_number,
        "learning_objective": learning_objective,
        "original_instruction": original_instruction,
        "required_strategy": required_strategy,
        "difficult_words": difficult_words,
        "protected_answers": protected_answers
    }
