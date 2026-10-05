"""
Stage 26: Prompt Registry & Structured Tier Templates.
Implements versioned, structured prompt templates enforcing tier lexical budgets,
clause boundaries, and non-disclosure invariants.
"""

from typing import Dict, Any
from .schemas import SupportLevel


UNIVERSAL_SYSTEM_INSTRUCTION = """You are a specialized child language simplification assistant for young learners aged 4-8.
Your task is to simplify the provided English text according to the specified educational support tier.

MANDATORY RULES:
1. Preserve the core pedagogical task intent and response mode.
2. Preserve exact named entities, quantities, numbers, colours, shapes, negation, and spatial/temporal relations.
3. Preserve the exact action sequence order.
4. DO NOT reveal answers, solutions, or distractor metadata.
5. DO NOT invent new facts or external context.
6. DO NOT convert statements into questions or change the activity format.
7. Return English text only, strictly adhering to the requested format.
"""

TIER_INSTRUCTIONS = {
    SupportLevel.MILD: """TIER: MILD SUPPORT
- Replace only the most difficult words with simpler familiar synonyms.
- Keep sentences natural and mostly intact; split only overly long compound structures (>15 words).
- Maintain single-sentence or natural instruction format.
""",
    SupportLevel.MODERATE: """TIER: MODERATE SUPPORT
- Replace complex vocabulary with age-appropriate everyday words.
- Unpack passive voice into active voice; simplify nominalizations.
- Split compound sentences into shorter direct clauses (<=10 words per clause).
- If the text contains verified multiple sequential actions, format them as numbered steps. Single-action instructions remain one direct sentence.
""",
    SupportLevel.STRONG: """TIER: STRONG SUPPORT
- Aggressively simplify vocabulary to basic high-frequency core words suitable for early readers.
- Break compound sentences into short, atomic direct clauses (<=7 words per clause).
- MANDATORY: If the text contains verified multiple sequential actions, you MUST format them as numbered steps (1. ..., 2. ...). Single-action instructions MUST remain one short direct instruction.
"""
}


class PromptRegistry:
    """Manages versioned prompt templates for multi-tier simplification."""
    VERSION = "1.0.0"

    @classmethod
    def get_prompt(cls, text: str, support_level: SupportLevel, protected_elements: list) -> str:
        tier_rule = TIER_INSTRUCTIONS.get(support_level, TIER_INSTRUCTIONS[SupportLevel.MODERATE])
        protected_clause = ""
        if protected_elements:
            protected_clause = f"\nPROTECTED ELEMENTS (MUST PRESERVE EXACTLY): {', '.join(protected_elements)}\n"

        prompt = f"""{UNIVERSAL_SYSTEM_INSTRUCTION}

{tier_rule}
{protected_clause}
INPUT TEXT:
{text}

SIMPLIFIED OUTPUT:"""
        return prompt.strip()
