"""Deterministic text normalization for external dataset evaluation."""

import hashlib
import unicodedata
from typing import List, Tuple


def normalize_text_for_evaluation(text: str) -> str:
    """Applies standard NFC unicode normalization and whitespace cleanup for evaluation.
    
    Preserves original characters while ensuring canonical unicode representation
    and consistent single-space whitespace. Does NOT alter spelling or grammar.
    """
    if not text:
        return ""
    
    # 1. NFC Unicode normalization
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Whitespace standardization (collapse tabs/multiple spaces, strip ends)
    normalized = " ".join(normalized.split())
    
    return normalized


def compute_deterministic_content_hash(
    source_text: str,
    references: List[str],
) -> str:
    """Computes SHA-256 hash over normalized source text and ordered references."""
    hasher = hashlib.sha256()
    hasher.update(source_text.encode("utf-8"))
    for ref in references:
        hasher.update(b"\x1f")  # unit separator delimiter
        hasher.update(ref.encode("utf-8"))
    return hasher.hexdigest()


def process_dual_text_representation(
    raw_source: str,
    raw_refs: List[str],
) -> Tuple[str, List[str], str]:
    """Generates evaluation view while preserving raw strings and computing hash."""
    eval_source = normalize_text_for_evaluation(raw_source)
    eval_refs = [normalize_text_for_evaluation(ref) for ref in raw_refs]
    content_hash = compute_deterministic_content_hash(eval_source, eval_refs)
    return eval_source, eval_refs, content_hash
