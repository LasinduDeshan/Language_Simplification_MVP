"""
Stage 26 Versioned Prompt Registry.
Provides tier-controlled prompt templates for Mild, Moderate, and Strong English language simplification.
"""
from typing import Dict, Any


class PromptRegistry:
    """
    Manages versioned, structured prompt templates for generative models.
    """

    VERSION = "2.1.0"

    TIER_INSTRUCTIONS = {
        "mild": (
            "You are a child-friendly language assistant for young learners aged 4 to 8.\n"
            "Task: Mildly simplify the following instruction.\n"
            "- Simplify only unnecessarily difficult vocabulary.\n"
            "- Keep sentence structure natural and mostly unchanged.\n"
            "- STRICT INVARIANT: Preserve all names, quantities, colors, shapes, action order, and negation.\n"
            "- STRICT INVARIANT: Do NOT reveal or give away the answer to the task.\n"
            "- Output ONLY the simplified English sentence with no commentary."
        ),
        "moderate": (
            "You are a child-friendly language assistant for young learners aged 4 to 8.\n"
            "Task: Moderately simplify the following instruction.\n"
            "- Replace complex words with everyday vocabulary suitable for ages 4-6.\n"
            "- Break compound or complex sentences into simpler clauses.\n"
            "- If multiple actions exist, format them clearly.\n"
            "- STRICT INVARIANT: Preserve all names, quantities, colors, shapes, action order, and negation.\n"
            "- STRICT INVARIANT: Do NOT reveal or give away the answer to the task.\n"
            "- Output ONLY the simplified English text with no commentary."
        ),
        "strong": (
            "You are a child-friendly language assistant for young learners aged 4 to 8.\n"
            "Task: Strongly simplify the following instruction to maximize clarity.\n"
            "- Use short, direct, atomic sentences with basic vocabulary.\n"
            "- Number all multi-step actions (e.g., '1. ... 2. ...').\n"
            "- Make subject and objects explicit in every step.\n"
            "- STRICT INVARIANT: Preserve all names, quantities, colors, shapes, action order, and negation.\n"
            "- STRICT INVARIANT: Do NOT reveal or give away the answer to the task.\n"
            "- Output ONLY the simplified English text with no commentary."
        ),
    }

    @classmethod
    def get_prompt(cls, text: str, support_level: str, exact_preservation: list = None) -> str:
        tier = support_level.lower()
        base_inst = cls.TIER_INSTRUCTIONS.get(tier, cls.TIER_INSTRUCTIONS["moderate"])
        
        preservation_clause = ""
        if exact_preservation:
            terms = ", ".join(f"'{t}'" for t in exact_preservation)
            preservation_clause = f"\nMandatory Exact Words to Keep: {terms}\n"

        prompt = (
            f"{base_inst}\n"
            f"{preservation_clause}\n"
            f"Original Text: \"{text}\"\n"
            f"Simplified Text:"
        )
        return prompt

    @classmethod
    def export_markdown(cls) -> str:
        md = f"""# Stage 26 Prompt Registry

**Version:** {cls.VERSION}  
**Status:** Approved  
**Language:** English (Ages 4–8)  

---

## 1. Prompt Design Invariants
1. **English Output Only:** All generated text must be valid English.
2. **Preservation Invariant:** Exact preservation of names, numbers, colors, shapes, negation, relations, and action order.
3. **Zero Answer Disclosure:** No answers or hints toward solutions.
4. **Structured Format:** Output only the clean simplified text without markdown wrappers or conversational filler.

---

## 2. Tier-Specific Instructions

### Mild Tier
```text
{cls.TIER_INSTRUCTIONS['mild']}
```

### Moderate Tier
```text
{cls.TIER_INSTRUCTIONS['moderate']}
```

### Strong Tier
```text
{cls.TIER_INSTRUCTIONS['strong']}
```
"""
        return md
