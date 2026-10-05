"""
Stage 26: Controlled Surface Repair Module.
Applies allowlisted surface repairs (whitespace, punctuation, casing, fence stripping)
without altering underlying semantic AST structures.
"""

import re
from typing import Tuple


def apply_controlled_surface_repair(text: str) -> Tuple[str, bool]:
    """
    Applies allowlisted surface normalization:
    1. Strips markdown code blocks (e.g. ```json ... ``` or ```text ... ```)
    2. Normalizes multiple consecutive spaces / newlines
    3. Fixes duplicate trailing punctuation (e.g. '..', '??')
    4. Capitalizes initial characters of sentences / numbered items
    Returns (repaired_text, repair_was_applied).
    """
    original = text
    repaired = text.strip()

    # 1. Strip markdown fences
    if repaired.startswith("```"):
        repaired = re.sub(r"^```(?:json|text)?\n?", "", repaired)
        repaired = re.sub(r"\n?```$", "", repaired).strip()

    # 2. Normalize whitespace
    repaired = re.sub(r"[ \t]+", " ", repaired)
    repaired = re.sub(r"\n{3,}", "\n\n", repaired)

    # 3. Fix duplicate punctuation
    repaired = re.sub(r"\.{2,}", ".", repaired)
    repaired = re.sub(r"\?{2,}", "?", repaired)
    repaired = re.sub(r"!{2,}", "!", repaired)

    # 4. Fix step numbering casing (e.g. '1. pick' -> '1. Pick')
    lines = repaired.split("\n")
    fixed_lines = []
    for line in lines:
        line = line.strip()
        m = re.match(r"^(\d+\.\s*)([a-z])(.*)$", line)
        if m:
            fixed_lines.append(f"{m.group(1)}{m.group(2).upper()}{m.group(3)}")
        else:
            if line and line[0].islower():
                fixed_lines.append(line[0].upper() + line[1:])
            else:
                fixed_lines.append(line)
    repaired = "\n".join(fixed_lines)

    changed = (repaired != original)
    return (repaired, changed)
