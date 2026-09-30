"""
B3: Syntactic Rule Baseline.
Applies allowlisted syntactic transformations (passive-to-active with explicit agent, nominalization unpacking) and routes ambiguous cases.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
import spacy
from app.baseline_simplification.schemas import BaselineMethodId
from app.baseline_simplification.output_validator import OutputValidator

NOMINALIZATION_MAP = {
    "make a decision": "decide",
    "made a decision": "decided",
    "makes a decision": "decides",
    "making a decision": "deciding",
    "give an explanation": "explain",
    "gave an explanation": "explained",
    "gives an explanation": "explains",
    "giving an explanation": "explaining",
    "have an argument": "argue",
    "had an argument": "argued",
    "has an argument": "argues",
    "take a look": "look",
    "took a look": "looked",
    "takes a look": "looks",
    "come to an agreement": "agree",
    "came to an agreement": "agreed",
}

class SyntacticRuleBaseline:
    """Applies allowlisted syntactic transformations with precondition safety checks."""

    def __init__(self, nlp: Optional[Any] = None):
        self.method_id = BaselineMethodId.B3
        self.method_version = "1.0.0"
        
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = spacy.blank("en")
        
        self.validator = OutputValidator(nlp=self.nlp)

    def _convert_passive_to_active(self, text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Converts passive sentences with explicit agent ('was X by Y') to active voice."""
        doc = self.nlp(text)
        
        # Look for passive auxiliary ('was', 'were', 'is', 'are') + past participle + 'by' agent
        pattern = re.compile(
            r"^(The|A|An|[A-Z][a-z]+)\s+([a-z\s]+?)\s+(was|were|is|are)\s+([a-z]+ed|[a-z]+en|caught|built|seen|made|found|eaten|read|drawn)\s+by\s+([A-Z][a-z]+|the\s+[a-z]+|a\s+[a-z]+)([\.!\?]?)$",
            re.IGNORECASE
        )
        match = pattern.match(text.strip())
        if match:
            art_subj, subject_noun, aux, verb_part, agent, punct = match.groups()
            punct = punct or "."
            full_subj = f"{art_subj} {subject_noun}".strip()
            
            # Format active sentence: Agent + Verb + Subject
            active_verb = verb_part.lower()
            agent_cap = agent[0].upper() + agent[1:]
            active_sentence = f"{agent_cap} {active_verb} {full_subj.lower()}{punct}"
            
            valid, _ = self.validator.validate_sentence(active_sentence)
            if valid:
                return active_sentence, {
                    "rule_id": "SYN-01-PASSIVE-ACTIVE",
                    "original_passive": text.strip(),
                    "agent": agent,
                    "verb": active_verb,
                    "target": full_subj,
                }

        return None, None

    def _unpack_nominalizations(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Unpacks abstract nominalizations into simple active verbs."""
        transformed = text
        applied_rules: List[Dict[str, Any]] = []

        for nom_phrase, verb_replacement in NOMINALIZATION_MAP.items():
            pattern = re.compile(rf"\b{re.escape(nom_phrase)}\b", re.IGNORECASE)
            if pattern.search(transformed):
                transformed = pattern.sub(verb_replacement, transformed)
                applied_rules.append({
                    "rule_id": "SYN-03-NOMINALIZATION-UNPACK",
                    "nominalization": nom_phrase,
                    "replacement": verb_replacement,
                })

        return transformed, applied_rules

    def simplify(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Applies allowlisted syntactic rules in sequence."""
        cleaned = text.strip()
        rules_applied: List[Dict[str, Any]] = []
        operation_outcomes: List[Dict[str, Any]] = []

        # 1. Passive to Active
        passive_res, passive_details = self._convert_passive_to_active(cleaned)
        current_text = passive_res if passive_res else cleaned
        if passive_res and passive_details:
            rules_applied.append({
                "rule_id": passive_details["rule_id"],
                "step": len(rules_applied) + 1,
                "details": passive_details,
            })
            operation_outcomes.append({
                "rule_id": passive_details["rule_id"],
                "outcome": "applied",
            })

        # 2. Nominalization Unpacking
        nom_res, nom_rules = self._unpack_nominalizations(current_text)
        current_text = nom_res
        for n_rule in nom_rules:
            rules_applied.append({
                "rule_id": n_rule["rule_id"],
                "step": len(rules_applied) + 1,
                "details": n_rule,
            })
            operation_outcomes.append({
                "rule_id": n_rule["rule_id"],
                "outcome": "applied",
            })

        return {
            "output_text": current_text,
            "rules_applied": rules_applied,
            "operation_outcomes": operation_outcomes,
            "fallback_used": False,
        }
