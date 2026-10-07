"""
Rule registry and configuration hash generator for Stage 25.
"""

import hashlib
import json
from typing import Dict, List, Any


RULE_CATALOGUE: List[Dict[str, Any]] = [
    {
        "rule_id": "ACT_TEMPORAL_UNROLL",
        "category": "action_graph",
        "description": "Reorders inverted temporal clauses (e.g. 'Before X, do Y') into chronological execution sequence.",
        "version": "1.0.0"
    },
    {
        "rule_id": "ACT_NUMBERED_STEPS",
        "category": "action_graph",
        "description": "Formats multi-action instructions into numbered atomic steps (1. Step one. 2. Step two.).",
        "version": "1.0.0"
    },
    {
        "rule_id": "ACT_MODIFIER_PROTECT",
        "category": "action_graph",
        "description": "Preserves safety-critical and task-critical modifiers on their associated action nodes.",
        "version": "1.0.0"
    },
    {
        "rule_id": "SYN_PASSIVE_TO_ACTIVE",
        "category": "syntactic",
        "description": "Converts passive voice with explicit agent into active voice.",
        "version": "1.0.0"
    },
    {
        "rule_id": "SYN_NOMINALIZATION_UNPACK",
        "category": "syntactic",
        "description": "Unpacks abstract nominalizations into simple direct verbs (e.g. 'make a choice' -> 'choose').",
        "version": "1.0.0"
    },
    {
        "rule_id": "SYN_CLAUSE_SPLIT",
        "category": "syntactic",
        "description": "Splits long compound and coordinated sentences at safe conjunction boundaries.",
        "version": "1.0.0"
    },
    {
        "rule_id": "SYN_EXPLICIT_SUBJECT",
        "category": "syntactic",
        "description": "Re-inserts explicit grammatical subject in split coordinated clauses.",
        "version": "1.0.0"
    },
    {
        "rule_id": "LEX_SUB_AGE_APPROPRIATE",
        "category": "lexical",
        "description": "Substitutes words exceeding target-age complexity using governed lexicon and allowlisted equivalents.",
        "version": "1.0.0"
    },
    {
        "rule_id": "LEX_MORPH_REPAIR",
        "category": "lexical",
        "description": "Repairs verb tense, subject-verb agreement, and determiners after lexical substitution.",
        "version": "1.0.0"
    },
    {
        "rule_id": "VOCAB_DEF_ATTACH",
        "category": "vocabulary_support",
        "description": "Attaches governed child-friendly definitions and contextual examples for complex domain words.",
        "version": "1.0.0"
    }
]


def get_rule_catalogue() -> List[Dict[str, Any]]:
    """Return the complete governed rule catalogue."""
    return RULE_CATALOGUE


def compute_configuration_hash() -> str:
    """Generate SHA-256 hash representing the frozen Stage 25 rule catalogue and parameters."""
    catalogue_json = json.dumps(RULE_CATALOGUE, sort_keys=True)
    return hashlib.sha256(catalogue_json.encode("utf-8")).hexdigest()
