"""
Protected elements configuration, semantic equivalence maps, and hash-based answer protection.
"""

import hashlib
import re
from typing import List, Dict, Set, Optional
from app.controlled_simplification.schemas import (
    ProtectedElementsConfig,
    SemanticEquivalenceRule,
    ModifierCriticality
)

# Standard allowlisted semantic equivalents for child simplification
DEFAULT_SEMANTIC_EQUIVALENCE_MAP: Dict[str, List[str]] = {
    "select": ["pick", "choose"],
    "choose": ["pick", "select"],
    "inside": ["in", "into"],
    "outside": ["out", "out of"],
    "underneath": ["under", "below"],
    "beneath": ["under", "below"],
    "adjacent to": ["next to", "beside"],
    "locate": ["find", "spot"],
    "purchase": ["buy", "get"],
    "obtain": ["get", "take"],
    "commence": ["start", "begin"],
    "construct": ["build", "make"],
    "examine": ["look at", "check"],
    "utilize": ["use"],
    "demonstrate": ["show"],
    "indicate": ["show", "point to"],
    "place": ["put", "set"],
    "position": ["put", "place"],
    "revolve": ["turn", "spin"],
    "terminate": ["stop", "end"],
    "smaller": ["little", "tiny", "small"],
    "larger": ["big", "giant", "large"],
    "huge": ["big", "large"],
    "tiny": ["small", "little"]
}

# Standard perceptual color and shape tokens
KNOWN_COLORS: Set[str] = {
    "red", "blue", "green", "yellow", "orange", "purple", "pink", "black", "white", "brown", "gray", "grey"
}

KNOWN_SHAPES: Set[str] = {
    "circle", "square", "triangle", "rectangle", "diamond", "star", "heart", "oval", "box", "ball", "cube"
}

# Modifiers categorized by safety and task criticality
SAFETY_CRITICAL_MODIFIERS: Set[str] = {
    "gently", "carefully", "slowly", "quietly", "safely", "smoothly"
}


def build_default_protected_config() -> ProtectedElementsConfig:
    """Build a default ProtectedElementsConfig with standard semantic equivalence rules."""
    rules = [
        SemanticEquivalenceRule(source=src, allowed=alw)
        for src, alw in DEFAULT_SEMANTIC_EQUIVALENCE_MAP.items()
    ]
    return ProtectedElementsConfig(
        exact_preservation=[],
        semantic_equivalence_allowed=rules,
        quantities=[],
        forbidden_disclosure_refs=[],
        forbidden_disclosure_hashes=[]
    )


def is_semantically_equivalent(source_token: str, target_token: str, custom_rules: Optional[List[SemanticEquivalenceRule]] = None) -> bool:
    """
    Check if target_token is an allowlisted semantic equivalent of source_token.
    """
    s = source_token.strip().lower()
    t = target_token.strip().lower()
    if s == t:
        return True

    # Check custom rules first
    if custom_rules:
        for rule in custom_rules:
            if rule.source.lower() == s and t in [a.lower() for a in rule.allowed]:
                return True

    # Check default equivalence map
    allowed = DEFAULT_SEMANTIC_EQUIVALENCE_MAP.get(s, [])
    return t in allowed


def hash_token(token: str) -> str:
    """Compute SHA-256 hash of a normalized token."""
    return f"sha256:{hashlib.sha256(token.strip().lower().encode('utf-8')).hexdigest()}"


def check_forbidden_disclosure_hashes(text: str, forbidden_hashes: List[str]) -> List[str]:
    """
    Verify that no word or n-gram in text hashes to a forbidden disclosure hash.
    Returns list of matching hashes if any violation occurs.
    """
    if not forbidden_hashes:
        return []

    forbidden_set = set(forbidden_hashes)
    words = re.findall(r"\b\w+\b", text.lower())
    violations = []

    # Check unigrams, bigrams, trigrams
    for n in range(1, min(4, len(words) + 1)):
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i : i + n])
            h = hash_token(ngram)
            if h in forbidden_set:
                violations.append(h)

    return violations
