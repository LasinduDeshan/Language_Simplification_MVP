"""Feature registry, metadata definitions, and allowlist validation for Stage 22."""

from typing import Dict, List, Set, Any, Tuple
import pandas as pd
from pathlib import Path


FEATURE_DEFINITIONS: List[Dict[str, Any]] = [
    # 1. Surface & Structural Complexity
    {"name": "char_count", "group": "surface", "type": "numeric_continuous", "description": "Total character count in normalized text"},
    {"name": "token_count", "group": "surface", "type": "numeric_continuous", "description": "Total token count including punctuation"},
    {"name": "word_count", "group": "surface", "type": "numeric_continuous", "description": "Total alphanumeric word count"},
    {"name": "sentence_count", "group": "surface", "type": "numeric_continuous", "description": "Total sentence count"},
    {"name": "punct_count", "group": "surface", "type": "numeric_continuous", "description": "Total punctuation token count"},
    {"name": "avg_word_length", "group": "surface", "type": "numeric_continuous", "description": "Average character length per word"},
    {"name": "avg_sentence_length", "group": "surface", "type": "numeric_continuous", "description": "Average token length per sentence"},
    {"name": "syllable_count", "group": "surface", "type": "numeric_continuous", "description": "Estimated total syllable count"},
    {"name": "avg_syllables_per_word", "group": "surface", "type": "numeric_continuous", "description": "Average syllable count per word"},
    {"name": "long_word_count", "group": "surface", "type": "numeric_continuous", "description": "Count of words with >= 7 characters or >= 3 syllables"},
    {"name": "long_word_ratio", "group": "surface", "type": "numeric_continuous", "description": "Ratio of long words to total words"},
    {"name": "type_token_ratio", "group": "surface", "type": "numeric_continuous", "description": "Lexical diversity ratio (unique lemmas / total tokens)"},

    # 2. Lexical & Part-of-Speech Complexity
    {"name": "noun_count", "group": "lexical_pos", "type": "numeric_continuous", "description": "Count of noun tokens"},
    {"name": "noun_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of noun tokens to total words"},
    {"name": "verb_count", "group": "lexical_pos", "type": "numeric_continuous", "description": "Count of verb tokens"},
    {"name": "verb_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of verb tokens to total words"},
    {"name": "adj_count", "group": "lexical_pos", "type": "numeric_continuous", "description": "Count of adjective tokens"},
    {"name": "adj_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of adjective tokens to total words"},
    {"name": "adv_count", "group": "lexical_pos", "type": "numeric_continuous", "description": "Count of adverb tokens"},
    {"name": "adv_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of adverb tokens to total words"},
    {"name": "content_word_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of content words (NOUN, VERB, ADJ, ADV) to total words"},
    {"name": "function_word_ratio", "group": "lexical_pos", "type": "numeric_continuous", "description": "Ratio of function words to total words"},

    # 3. Syntactic & Parse-Tree Complexity
    {"name": "max_dependency_depth", "group": "syntactic", "type": "numeric_continuous", "description": "Maximum parse-tree dependency depth"},
    {"name": "avg_dependency_depth", "group": "syntactic", "type": "numeric_continuous", "description": "Average parse-tree dependency depth across tokens"},
    {"name": "clause_count", "group": "syntactic", "type": "numeric_continuous", "description": "Count of subordinate/coordinate clauses"},
    {"name": "passive_voice", "group": "syntactic", "type": "binary", "description": "Binary indicator for detected passive voice constructions"},

    # 4. Semantic & Pedagogical Load
    {"name": "negation_count", "group": "semantic_load", "type": "numeric_continuous", "description": "Count of explicit and conditional negation markers"},
    {"name": "quantity_count", "group": "semantic_load", "type": "numeric_continuous", "description": "Count of numeric digits and quantity terms"},
]

FEATURE_NAMES: List[str] = [f["name"] for f in FEATURE_DEFINITIONS]
FEATURE_ALLOWLIST: Set[str] = set(FEATURE_NAMES)

CONTINUOUS_FEATURE_NAMES: List[str] = [f["name"] for f in FEATURE_DEFINITIONS if f["type"] == "numeric_continuous"]
BINARY_FEATURE_NAMES: List[str] = [f["name"] for f in FEATURE_DEFINITIONS if f["type"] == "binary"]

PROHIBITED_FEATURE_SUBSTRINGS: Set[str] = {
    "learner", "user_id", "child_id", "screening", "risk_level",
    "dld", "clinical", "score", "attempt", "accuracy_score",
    "label", "difficulty", "target", "gold", "answer",
}


def validate_feature_allowlist(column_names: List[str]) -> Tuple[bool, List[str]]:
    """Validates that extracted feature columns strictly conform to allowlist and contain 0 prohibited signals."""
    violations: List[str] = []
    for col in column_names:
        if col not in FEATURE_ALLOWLIST:
            violations.append(f"Unregistered feature column: {col}")
        for prohibited in PROHIBITED_FEATURE_SUBSTRINGS:
            if prohibited in col.lower():
                violations.append(f"Prohibited leakage substring '{prohibited}' in feature column: {col}")
    return len(violations) == 0, violations


def export_feature_dictionary(output_path: Path) -> pd.DataFrame:
    """Exports the authoritative stage22_feature_dictionary.csv."""
    df = pd.DataFrame(FEATURE_DEFINITIONS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df
