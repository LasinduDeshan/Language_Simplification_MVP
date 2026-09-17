import re
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional

class AnswerLeakageDetector:
    """
    Relation-aware answer leakage detector.
    Analyzes child instructions against task protected_answers and answer_presentation_policy.
    Distinguishes between:
    - Scaffolding candidate options (e.g. 'Choose: water or tree?' -> ALLOWED when policy allows candidate options)
    - Solution assertions (e.g. 'The fish lives in water' or 'Put fish in water' -> LEAKAGE)
    - Direct directives (e.g. 'The answer is water' or 'Tap the water' -> LEAKAGE)
    """

    DIRECT_ANSWER_PATTERNS = [
        r"\bthe\s+(?:correct\s+|right\s+)?answer\s+is\b",
        r"\bthe\s+(?:correct\s+|right\s+)?solution\s+is\b",
        r"\bthe\s+right\s+one\s+is\b",
        r"\bthe\s+correct\s+one\s+is\b",
    ]

    BINDING_CONNECTORS = [
        r"\bin\b", r"\binto\b", r"\bon\b", r"\bto\b", r"\bunder\b",
        r"\blives?\s+in\b", r"\bgoes?\s+(?:in|into|to|on)\b",
        r"\bbelongs?\s+(?:in|to|on)\b", r"\bput\b", r"\bplace\b", r"\bpack\b"
    ]

    def _normalize_text(self, text: str) -> str:
        """Removes extra whitespace and punctuation for canonical comparison."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def check_leakage(self, instruction: str, task: Any) -> Dict[str, Any]:
        """
        Evaluates instruction against task protected answers.
        Returns:
            is_leaked: bool
            leakage_type: Optional[str] ("restricted_phrase", "relation_binding", "direct_solution_directive", "disallowed_candidate_mention")
            leaked_items: List[str]
            similarity_score: float
            details: str
        """
        if not instruction or not task:
            return {
                "is_leaked": False,
                "leakage_type": None,
                "leaked_items": [],
                "similarity_score": 0.0,
                "details": "No instruction or task provided"
            }

        norm_instruction = self._normalize_text(instruction)
        orig_instruction = instruction.lower()

        # Extract protected answers & policies from task (supports Task model or dict)
        prot = getattr(task, "protected_answers", None)
        if prot is None and isinstance(task, dict):
            prot = task.get("protected_answers", {})
        elif prot is None:
            prot = {}

        policy = getattr(task, "answer_presentation_policy", None)
        if policy is None and isinstance(task, dict):
            policy = task.get("answer_presentation_policy", {})
        elif policy is None:
            policy = {}

        restricted_phrases = prot.get("restricted_solution_phrases", [])
        relations = prot.get("relations", [])
        allowed_terms = set(term.lower() for term in prot.get("allowed_instruction_terms", []))
        candidate_answers_may_be_shown = policy.get("candidate_answers_may_be_shown", True)
        correct_candidate_may_be_identified = policy.get("correct_candidate_may_be_identified", False)

        leaked_items: List[str] = []
        highest_similarity = 0.0

        # -------------------------------------------------------------
        # 1. Check Direct Answer Directives
        # -------------------------------------------------------------
        for pat in self.DIRECT_ANSWER_PATTERNS:
            if re.search(pat, orig_instruction):
                return {
                    "is_leaked": True,
                    "leakage_type": "direct_solution_directive",
                    "leaked_items": ["direct_answer_phrase"],
                    "similarity_score": 1.0,
                    "details": "Instruction contains explicit answer revelation phrasing ('the answer is...')"
                }

        # -------------------------------------------------------------
        # 2. Check Restricted Solution Phrases
        # -------------------------------------------------------------
        for phrase in restricted_phrases:
            norm_phrase = self._normalize_text(phrase)
            # Exact or substring match on normalized strings
            if norm_phrase in norm_instruction or phrase.lower() in orig_instruction:
                return {
                    "is_leaked": True,
                    "leakage_type": "restricted_phrase",
                    "leaked_items": [phrase],
                    "similarity_score": 1.0,
                    "details": f"Instruction contains restricted solution phrase: '{phrase}'"
                }

            # Fuzzy similarity check against restricted phrase
            sim = SequenceMatcher(None, norm_phrase, norm_instruction).ratio()
            if sim > highest_similarity:
                highest_similarity = sim

            if sim >= 0.85:
                return {
                    "is_leaked": True,
                    "leakage_type": "restricted_phrase",
                    "leaked_items": [phrase],
                    "similarity_score": round(sim, 3),
                    "details": f"Instruction has high similarity ({sim:.2f}) to restricted solution phrase: '{phrase}'"
                }

        # -------------------------------------------------------------
        # 3. Check Subject-Relation-Answer Binding
        # -------------------------------------------------------------
        for rel in relations:
            subject = rel.get("subject", "").lower()
            relation_name = rel.get("relation", "").lower()
            answer = rel.get("answer", "").lower()

            if not subject or not answer:
                continue

            norm_subject = self._normalize_text(subject)
            norm_answer = self._normalize_text(answer)

            # Check if both subject and answer are mentioned
            subject_in_text = norm_subject in norm_instruction
            answer_in_text = norm_answer in norm_instruction

            if not (subject_in_text and answer_in_text):
                # If subject or answer not both in text, check individual answer directive
                # e.g., "tap the water" or "pick water" without alternative choices
                if answer_in_text and not correct_candidate_may_be_identified:
                    # Check if instruction is a directive to tap/pick only the correct answer
                    directive_match = re.search(
                        rf"\b(?:pick|choose|tap|select)\s+(?:the\s+)?{re.escape(norm_answer)}\b",
                        norm_instruction
                    )
                    # Make sure it's not a contrast like "choose water or tree"
                    has_contrast_or = re.search(r"\bor\b", norm_instruction)
                    if directive_match and not has_contrast_or:
                        return {
                            "is_leaked": True,
                            "leakage_type": "direct_solution_directive",
                            "leaked_items": [answer],
                            "similarity_score": 0.9,
                            "details": f"Directly instructs child to choose target answer '{answer}' without choice options"
                        }
                continue

            # Both subject and answer ARE in the text!
            # Check if they are bound in a solution statement
            # E.g. "put fish in water", "fish lives in water", "crayons in the box"
            is_choice_contrast = bool(re.search(r"\b(?:or)\b", norm_instruction) and re.search(r"\b(?:choose|pick|select|which|is it)\b", norm_instruction))

            # Look for binding patterns linking subject and answer
            # Pattern A: Subject ... (connector) ... Answer
            subj_ans_pattern = rf"\b{re.escape(norm_subject)}\b.*?\b(?:in|into|on|to|under|lives|live|goes|belongs|is|are|put|place)\b.*?\b{re.escape(norm_answer)}\b"
            # Pattern B: Action ... Subject ... (connector) ... Answer (e.g. "put crayons in box")
            action_binding_pattern = rf"\b(?:put|place|pack|move)\b.*?\b{re.escape(norm_subject)}\b.*?\b(?:in|into|on|to)\b.*?\b{re.escape(norm_answer)}\b"

            if re.search(subj_ans_pattern, norm_instruction) or re.search(action_binding_pattern, norm_instruction):
                # If it's pure binding, it's leakage even if "choose" appears elsewhere unless it's strictly a neutral question
                # E.g. "Put the fish in the water. Choose: water or tree" is still leakage!
                leaked_items.append(f"{subject} -> {answer}")
                return {
                    "is_leaked": True,
                    "leakage_type": "relation_binding",
                    "leaked_items": leaked_items,
                    "similarity_score": 0.95,
                    "details": f"Instruction asserts relation binding between subject '{subject}' and target answer '{answer}'"
                }

        # -------------------------------------------------------------
        # 4. Check Policy on Candidate Answer Presentation
        # -------------------------------------------------------------
        if not candidate_answers_may_be_shown:
            # Under this policy, no answer target may be mentioned before attempt
            for rel in relations:
                answer = rel.get("answer", "").lower()
                if answer and self._normalize_text(answer) in norm_instruction:
                    # Ignore if the answer is explicitly an allowed instruction term
                    if answer in allowed_terms:
                        continue
                    return {
                        "is_leaked": True,
                        "leakage_type": "disallowed_candidate_mention",
                        "leaked_items": [answer],
                        "similarity_score": 0.85,
                        "details": f"Candidate answer '{answer}' mentioned when policy forbids revealing candidates"
                    }

        return {
            "is_leaked": False,
            "leakage_type": None,
            "leaked_items": [],
            "similarity_score": round(highest_similarity, 3),
            "details": "No answer leakage detected; complies with answer presentation policy"
        }

answer_leakage_detector = AnswerLeakageDetector()
