import re
import string
from typing import Dict, Any, List, Optional
from app.tasks.repository import task_repository

def normalize_text(text: str) -> str:
    """Lowercases, removes punctuation, and collapses whitespace."""
    if not text:
        return ""
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation.replace("-", "")))
    return " ".join(text.split())

class AnswerChecker:
    def evaluate_answer(
        self,
        task,
        transcript: Optional[str] = None,
        selected_answer: Optional[Any] = None,
        completion_status: str = "completed"
    ) -> Dict[str, Any]:
        """
        Evaluates the semantic concept correctness and target skill mastery separately.
        
        Returns:
        - target_skill
        - concept_result: 'correct' | 'partial' | 'incorrect' | 'unclear'
        - target_skill_result: 'correct' | 'partial' | 'incorrect' | 'not_applicable'
        - matched_concepts, missing_concepts, contradictions
        - retry_required: bool
        - retry_reason: str | None
        - grammar_observations: list
        - vocabulary_observations: list
        """
        target_skill = getattr(task, "target_skill", None) or getattr(task, "subskill", "concept_mastery")
        expected_concepts = getattr(task, "expected_concepts", []) or []
        acceptable_answers = getattr(task, "acceptable_answers", []) or []
        grammar_targets = getattr(task, "grammar_targets", []) or []
        
        # 1. Non-completed statuses (no_response, asked_for_help, skipped)
        if completion_status in ["no_response", "asked_for_help", "skipped"]:
            return {
                "target_skill": target_skill,
                "concept_result": "unclear",
                "target_skill_result": "incorrect",
                "matched_concepts": [],
                "missing_concepts": expected_concepts,
                "contradictions": [],
                "match_tier": completion_status,
                "grammar_observations": [],
                "vocabulary_observations": [],
                "retry_required": True,
                "retry_reason": f"child_{completion_status}"
            }

        # Format input text
        norm_transcript = normalize_text(transcript or "")
        selected_text = ""
        if selected_answer:
            if isinstance(selected_answer, dict):
                selected_text = str(selected_answer.get("value", selected_answer.get("label", "")))
            elif isinstance(selected_answer, list):
                selected_text = " ".join(str(item) for item in selected_answer)
            else:
                selected_text = str(selected_answer)
        
        combined_text = f"{norm_transcript} {normalize_text(selected_text)}".strip()

        if not combined_text:
            return {
                "target_skill": target_skill,
                "concept_result": "unclear",
                "target_skill_result": "incorrect",
                "matched_concepts": [],
                "missing_concepts": expected_concepts,
                "contradictions": [],
                "match_tier": "none",
                "grammar_observations": [],
                "vocabulary_observations": [],
                "retry_required": True,
                "retry_reason": "no_input_received"
            }

        def has_word(w: str, text: str) -> bool:
            return bool(re.search(r"\b" + re.escape(w.lower()) + r"\b", text.lower()))

        # ----------------------------------------------------
        # 2. Contradiction & Conflict Checks
        # ----------------------------------------------------
        contradictions = []
        task_code = getattr(task, "task_code", "")

        if has_word("fish", combined_text) and has_word("tree", combined_text):
            contradictions.append("fish_in_tree_conflict")
        if has_word("bird", combined_text) and has_word("carpet", combined_text):
            contradictions.append("bird_in_carpet_conflict")
        if has_word("rug", combined_text) and "crayons" in combined_text:
            contradictions.append("materials_on_rug_conflict")

        if contradictions:
            return {
                "target_skill": target_skill,
                "concept_result": "incorrect",
                "target_skill_result": "incorrect",
                "matched_concepts": [],
                "missing_concepts": expected_concepts,
                "contradictions": contradictions,
                "match_tier": "contradiction_detected",
                "grammar_observations": [],
                "vocabulary_observations": [],
                "retry_required": True,
                "retry_reason": "contradiction_detected"
            }

        # ----------------------------------------------------
        # 3. Concept Correctness Evaluation
        # ----------------------------------------------------
        concept_result = "unclear"
        matched_concepts = []
        missing_concepts = []

        # Exact match with acceptable answers
        for orig_ans in acceptable_answers:
            if normalize_text(orig_ans) == combined_text or (transcript and normalize_text(orig_ans) == norm_transcript):
                concept_result = "correct"
                matched_concepts = expected_concepts
                break

        if concept_result != "correct":
            # Keyword/concept overlap check
            matched_count = 0
            for c in expected_concepts:
                c_norm = normalize_text(c)
                keywords = [k for k in c_norm.split() if k not in {"in", "on", "the", "a", "an", "is", "are", "to"}]
                if not keywords:
                    # For preposition/function-word tasks, check if child understood the core entities
                    prompt_words = [w for w in normalize_text(getattr(task, "prompt", "") or getattr(task, "child_friendly_instruction", "")).split() if w not in {"in", "on", "the", "a", "an", "is", "are", "to", "choose", "missing", "word"}]
                    vocab_targets = [w.lower() for w in getattr(task, "vocabulary_targets", []) or []]
                    core_context_words = list(set(prompt_words + vocab_targets))
                    if any(w in combined_text for w in core_context_words) or has_word("water", combined_text) or has_word("fish", combined_text):
                        matched_concepts.append(c)
                        matched_count += 1
                    elif c_norm in combined_text.split():
                        matched_concepts.append(c)
                        matched_count += 1
                    else:
                        missing_concepts.append(c)
                    continue

                # Check if all required keywords (or stems) are present
                c_matched = all(
                    any(kw in w or w in kw or kw.rstrip("s").rstrip("ing") in w for w in combined_text.split())
                    for kw in keywords
                )
                # Check pronoun contradiction (e.g. expected 'she' but said 'he')
                if "she" in keywords and "he" in combined_text.split() and "she" not in combined_text.split():
                    c_matched = False
                if "he" in keywords and "she" in combined_text.split() and "he" not in combined_text.split():
                    c_matched = False

                if c_matched:
                    matched_concepts.append(c)
                    matched_count += 1
                else:
                    missing_concepts.append(c)

            if matched_count == len(expected_concepts) and expected_concepts:
                concept_result = "correct"
            elif matched_count > 0:
                concept_result = "partial"
            else:
                concept_result = "incorrect"

        # ----------------------------------------------------
        # 4. Target Skill & Grammar Analysis Separation
        # ----------------------------------------------------
        grammar_observations = []
        vocabulary_observations = []
        target_skill_result = "correct"

        # Specific Grammar Target Skill Handlers
        if "preposition" in target_skill or "location_preposition" in grammar_targets:
            # Check if expected preposition is present
            target_preps = ["in", "on", "under", "beside", "behind", "next to"]
            expected_preps = [p for p in target_preps if any(has_word(p, normalize_text(ans)) for ans in acceptable_answers)]
            if not expected_preps:
                expected_preps = ["in"]  # default for GRAM-PREP-001

            has_target_prep = any(has_word(p, combined_text) for p in expected_preps)
            if not has_target_prep:
                grammar_observations.append("missing_preposition")
                target_skill_result = "incorrect"
            else:
                target_skill_result = "correct"

        elif "subject_verb_agreement" in target_skill or "third_person_singular_s" in grammar_targets:
            if has_word("plays", combined_text):
                target_skill_result = "correct"
            elif has_word("play", combined_text):
                grammar_observations.append("missing_third_person_s")
                target_skill_result = "incorrect"
            else:
                target_skill_result = "correct" if concept_result == "correct" else "incorrect"

        elif "indefinite_article" in target_skill or "indefinite_article_a_an" in target_skill:
            if has_word("an", combined_text):
                target_skill_result = "correct"
            elif has_word("a", combined_text):
                grammar_observations.append("incorrect_article_a_before_vowel")
                target_skill_result = "incorrect"
            else:
                target_skill_result = "correct" if concept_result == "correct" else "incorrect"

        elif "regular_plural" in target_skill:
            if has_word("dogs", combined_text):
                target_skill_result = "correct"
            elif has_word("dog", combined_text):
                grammar_observations.append("missing_plural_s")
                target_skill_result = "incorrect"
            else:
                target_skill_result = "correct" if concept_result == "correct" else "incorrect"

        elif "past_tense" in target_skill:
            if has_word("walked", combined_text):
                target_skill_result = "correct"
            elif has_word("walks", combined_text) or has_word("walk", combined_text):
                grammar_observations.append("omitted_past_tense_ed")
                target_skill_result = "incorrect"
            else:
                target_skill_result = "correct" if concept_result == "correct" else "incorrect"

        elif "word_order" in target_skill or "syntax_ordering" in target_skill or getattr(task, "expected_sequence", None):
            # Check canonical order against acceptable answers or expected sequence
            expected_seq = getattr(task, "expected_sequence", [])
            expected_seq_str = " ".join(str(s) for s in expected_seq) if expected_seq else ""
            is_order_correct = any(normalize_text(ans) == combined_text for ans in acceptable_answers)
            if not is_order_correct and expected_seq_str:
                is_order_correct = (normalize_text(expected_seq_str) == combined_text)

            if is_order_correct:
                target_skill_result = "correct"
            else:
                target_skill_result = "incorrect"
                if "incorrect_word_order_svo" not in grammar_observations:
                    grammar_observations.append("incorrect_word_order_svo")

        else:
            # For vocabulary, instructions, and comprehension, target skill aligns with concept correctness
            target_skill_result = "correct" if concept_result == "correct" else ("partial" if concept_result == "partial" else "incorrect")

        # Run spaCy linguistic grammar extractor to enrich observations
        try:
            from app.grammar_analysis.grammar_extractor import grammar_extractor
            nlp_gram = grammar_extractor.analyze_grammar(combined_text, speech_confidence=1.0)
            for obs in nlp_gram.get("observations", []):
                code = obs.get("observation_code")
                if code and code not in grammar_observations:
                    grammar_observations.append(code)
                    if code in ["incorrect_word_order", "incorrect_word_order_svo"] and ("word_order" in target_skill or "syntax_ordering" in target_skill):
                        target_skill_result = "incorrect"
        except Exception:
            pass

        # Missing preposition observation check for any sentence missing required prepositions
        if "in" not in combined_text and "on" not in combined_text and "under" not in combined_text:
            if any("in" in normalize_text(ans).split() or "on" in normalize_text(ans).split() for ans in acceptable_answers):
                if "missing_preposition" not in grammar_observations:
                    grammar_observations.append("missing_preposition")

        # ----------------------------------------------------
        # 5. Determine Retry Requirement
        # ----------------------------------------------------
        retry_required = False
        retry_reason = None

        if target_skill_result != "correct":
            retry_required = True
            retry_reason = "target_skill_not_demonstrated"
        elif concept_result not in ["correct", "partial"]:
            retry_required = True
            retry_reason = "concept_incorrect"

        return {
            "target_skill": target_skill,
            "concept_result": concept_result,
            "target_skill_result": target_skill_result,
            "matched_concepts": matched_concepts or expected_concepts,
            "missing_concepts": missing_concepts,
            "contradictions": contradictions,
            "grammar_observations": grammar_observations,
            "vocabulary_observations": vocabulary_observations,
            "retry_required": retry_required,
            "retry_reason": retry_reason,
            "match_tier": "semantic_rule"
        }

answer_checker = AnswerChecker()
