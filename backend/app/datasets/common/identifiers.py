"""
Identifier format validation and legacy ID preservation for Stage 14 datasets.
Supports owner prefixes: C1-, C2-, AR-, C3-, SIMP-, INT-, LEX-, plus valid Stage 13 legacy IDs.
"""
import re

# Standard V1 ID patterns
PATTERN_ADAPTATION_ACTIVITY = re.compile(r"^(C[123]|AR)-[A-Z]{2}-[A-Z0-9_\-]+$")
PATTERN_SIMPLIFICATION_PAIR = re.compile(r"^SIMP-[A-Z]{2}-\d{4,6}$")
PATTERN_INTERACTION_RECORD = re.compile(r"^INT-\d{8}-\d{6}$|^INT-[a-f0-9]{8}$")
PATTERN_LEXICON_ENTRY = re.compile(r"^LEX-[A-Z]{2}-\d{4,6}$")

# Stage 13 Legacy Valid Patterns (Preserved without rename)
PATTERN_STAGE13_LEGACY_TASK = re.compile(r"^(VOC|GRAM|COMP|INST)-[A-Z0-9_\-]+$")

def is_valid_activity_id(activity_id: str) -> bool:
    """Validates activity ID supporting multi-owner prefixes and Stage 13 legacy IDs."""
    if not activity_id or not isinstance(activity_id, str):
        return False
    if PATTERN_ADAPTATION_ACTIVITY.match(activity_id):
        return True
    if PATTERN_STAGE13_LEGACY_TASK.match(activity_id):
        return True
    # Allow C3-EN-<legacy_code>
    if activity_id.startswith("C3-EN-") or activity_id.startswith("C1-EN-") or activity_id.startswith("C2-EN-"):
        return True
    return False

def is_valid_pair_id(pair_id: str) -> bool:
    """Validates simplification pair ID."""
    if not pair_id or not isinstance(pair_id, str):
        return False
    return bool(PATTERN_SIMPLIFICATION_PAIR.match(pair_id))

def is_valid_interaction_id(interaction_id: str) -> bool:
    """Validates interaction record ID."""
    if not interaction_id or not isinstance(interaction_id, str):
        return False
    return bool(PATTERN_INTERACTION_RECORD.match(interaction_id))

def is_valid_lexicon_id(entry_id: str) -> bool:
    """Validates lexicon entry ID."""
    if not entry_id or not isinstance(entry_id, str):
        return False
    return bool(PATTERN_LEXICON_ENTRY.match(entry_id))
