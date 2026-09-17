import re
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher
from app.validation.answer_leakage import answer_leakage_detector
from app.validation.child_suitability import child_suitability_checker

class AdaptationValidator:
    """
    Multi-sequence validation orchestrator.
    Combines:
    - Answer Leakage Detection (relation-aware)
    - Child Suitability & Safety (prohibited terms, clinical jargon, sentence length)
    - Meaning Preservation (task goal alignment)
    - Support Level Compliance
    """

    def _calculate_meaning_preservation(self, instruction: str, task: Any) -> float:
        """
        Calculates semantic preservation score (0.0 to 1.0) by analyzing
        concept overlap between the adapted instruction and task objectives.
        """
        if not instruction or not task:
            return 0.5

        inst_words = set(re.findall(r"\b\w{3,}\b", instruction.lower()))

        # Target concept words from original instruction, expected concepts, learning objective
        target_texts = []
        orig = getattr(task, "original_instruction", "") or ""
        target_texts.append(orig)

        obj = getattr(task, "learning_objective", "") or ""
        target_texts.append(obj)

        expected = getattr(task, "expected_concepts", []) or []
        if isinstance(expected, list):
            target_texts.extend([str(e) for e in expected])

        vocab_targets = getattr(task, "vocabulary_targets", []) or []
        if isinstance(vocab_targets, list):
            target_texts.extend([str(v) for v in vocab_targets])

        prot = getattr(task, "protected_answers", {}) or {}
        if isinstance(prot, dict):
            allowed = prot.get("allowed_instruction_terms", [])
            target_texts.extend([str(a) for a in allowed])

        combined_targets = " ".join(target_texts).lower()
        target_words = set(re.findall(r"\b\w{3,}\b", combined_targets))

        # Basic action and question words common in simplified instructions
        scaffolding_words = {"look", "find", "put", "place", "pack", "choose", "pick", "where", "which", "what", "touch", "tap", "match", "help", "home", "bin", "box", "show"}

        if not target_words:
            return 0.90

        # Compute overlap
        overlap = inst_words.intersection(target_words.union(scaffolding_words))
        if not inst_words:
            return 0.0

        overlap_ratio = len(overlap) / len(inst_words)

        # Base similarity from SequenceMatcher against original instruction
        base_sim = SequenceMatcher(None, instruction.lower(), orig.lower()).ratio()

        # Weighted semantic preservation score
        semantic_score = min(1.0, max(0.40, (overlap_ratio * 0.7) + (base_sim * 0.3) + 0.25))
        return round(semantic_score, 2)

    def validate_candidate(
        self,
        task: Any,
        candidate_data: Dict[str, Any],
        learner: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Validates a candidate instruction output against all safety and developmental gates.
        Returns a dictionary suitable for populating a ValidationResult record.
        """
        instruction = candidate_data.get("child_instruction", "")
        supportive_msg = candidate_data.get("supportive_message", "")
        target_support = candidate_data.get("support_level", "moderate")

        failure_reasons: List[str] = []

        # 1. Basic Language Validity
        language_valid = bool(instruction and len(instruction.strip()) > 0 and len(instruction.split()) >= 2)
        if not language_valid:
            failure_reasons.append("invalid_instruction_text")

        # 2. Answer Leakage Check
        leakage_res = answer_leakage_detector.check_leakage(instruction, task)
        answer_leakage = leakage_res["is_leaked"]
        if answer_leakage:
            failure_reasons.append(f"answer_leakage_{leakage_res['leakage_type']}: {', '.join(leakage_res['leaked_items'])}")

        # 3. Child Suitability & Safety Check
        target_age = getattr(learner, "age", None) if learner else None
        suitability_res = child_suitability_checker.check_suitability(
            instruction=instruction,
            supportive_message=supportive_msg,
            target_age=target_age
        )
        safety_valid = suitability_res["safety_valid"]
        sentence_length_valid = suitability_res["sentence_length_valid"]

        for v in suitability_res["violations"]:
            failure_reasons.append(v)

        # 4. Meaning Preservation
        semantic_score = self._calculate_meaning_preservation(instruction, task)
        meaning_preserved = semantic_score >= 0.50
        if not meaning_preserved:
            failure_reasons.append(f"meaning_not_preserved: score {semantic_score:.2f} < 0.50")

        # 5. Age Appropriateness & Support Level
        age_appropriate = safety_valid and sentence_length_valid
        support_level_valid = target_support in ["mild", "moderate", "strong"]

        # Status resolution
        is_approved = (
            language_valid and
            not answer_leakage and
            safety_valid and
            sentence_length_valid and
            meaning_preserved and
            support_level_valid
        )

        status = "approved" if is_approved else "rejected"

        return {
            "language_valid": language_valid,
            "age_appropriate": age_appropriate,
            "meaning_preserved": meaning_preserved,
            "answer_leakage": answer_leakage,
            "sentence_length_valid": sentence_length_valid,
            "support_level_valid": support_level_valid,
            "safety_valid": safety_valid,
            "average_words_per_sentence": suitability_res["average_words_per_sentence"],
            "maximum_words_in_sentence": suitability_res["maximum_words_in_sentence"],
            "semantic_score": semantic_score,
            "status": status,
            "failure_reasons": failure_reasons,
            "leakage_details": leakage_res,
            "suitability_details": suitability_res
        }

adaptation_validator = AdaptationValidator()
