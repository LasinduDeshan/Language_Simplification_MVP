import re
import string
from typing import Dict, Any, List, Optional
from app.tasks.repository import task_repository

def normalize_text(text: str) -> str:
    """Lowercases, removes punctuation, and collapses whitespace."""
    if not text:
        return ""
    text = text.lower().strip()
    # Remove punctuation except hyphens inside words
    text = text.translate(str.maketrans("", "", string.punctuation.replace("-", "")))
    return " ".join(text.split())

class AnswerChecker:
    def evaluate_answer(
        self,
        task,
        transcript: Optional[str],
        selected_answer: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates the semantic concept correctness of a child's response.
        Separates factual/conceptual correctness from grammatical errors.
        """
        if not transcript and not selected_answer:
            return {
                "concept_result": "unclear",
                "matched_concepts": [],
                "missing_concepts": task.expected_concepts if hasattr(task, "expected_concepts") else [],
                "contradictions": [],
                "match_tier": "none"
            }

        norm_transcript = normalize_text(transcript or "")
        
        # Also incorporate selected answer keys if provided (e.g., choice tap)
        if selected_answer:
            ans_val = str(selected_answer.get("value", selected_answer.get("label", "")))
            if ans_val:
                norm_transcript = f"{norm_transcript} {normalize_text(ans_val)}".strip()

        acceptable_answers = task.acceptable_answers or []
        normalized_acceptable = [normalize_text(ans) for ans in acceptable_answers]
        expected_concepts = task.expected_concepts or []
        prot = task.protected_answers or {}
        relations = prot.get("relations", [])

        # ----------------------------------------------------
        # Tier 1: Contradiction & Conflict Checks (Run First!)
        # ----------------------------------------------------
        contradictions = []
        task_code = getattr(task, "task_code", "")

        def has_word(w: str, text: str) -> bool:
            return bool(re.search(r"\b" + re.escape(w) + r"\b", text))

        # Task 2 (Habitat): Fish cannot be in tree; bird cannot be in water
        if has_word("fish", norm_transcript) and has_word("tree", norm_transcript):
            contradictions.append("fish_in_tree_conflict")
        if has_word("bird", norm_transcript) and has_word("water", norm_transcript):
            contradictions.append("bird_in_water_conflict")

        # Task 1 (Clean up): Paper cannot be on rug
        if has_word("rug", norm_transcript):
            contradictions.append("paper_placed_on_rug")

        # Task 6 (Cat under desk): Cat cannot be on chair
        if has_word("chair", norm_transcript) and not has_word("desk", norm_transcript):
            contradictions.append("cat_on_chair_conflict")

        # Task 8 (Leo sleeping): Mouse was not sleeping
        if has_word("mouse", norm_transcript) and ("sleep" in norm_transcript or "nap" in norm_transcript):
            contradictions.append("mouse_sleeping_conflict")

        # Task 9 (Pronoun): Target is girl (she); "he" is contradictory
        if task_code == "TASK-ENG-009":
            if has_word("he", norm_transcript) and not has_word("she", norm_transcript):
                contradictions.append("incorrect_gender_pronoun_he")

        if contradictions:
            return {
                "concept_result": "incorrect",
                "matched_concepts": [],
                "missing_concepts": expected_concepts,
                "contradictions": contradictions,
                "match_tier": "contradiction_detected"
            }

        # ----------------------------------------------------
        # Tier 2: Exact & Discrete Normalized Match
        # ----------------------------------------------------
        for orig_ans in acceptable_answers:
            if transcript and transcript.strip().lower() == orig_ans.lower():
                return {
                    "concept_result": "correct",
                    "matched_concepts": expected_concepts,
                    "missing_concepts": [],
                    "contradictions": [],
                    "match_tier": "exact"
                }

        for norm_ans in normalized_acceptable:
            if norm_transcript == norm_ans:
                return {
                    "concept_result": "correct",
                    "matched_concepts": expected_concepts,
                    "missing_concepts": [],
                    "contradictions": [],
                    "match_tier": "normalized"
                }

        # ----------------------------------------------------
        # Tier 3: Relation Triplet Evaluation
        # ----------------------------------------------------
        if relations:
            matched_relations = []
            failed_relations = []

            for rel in relations:
                subj = normalize_text(rel.get("subject", ""))
                ans = normalize_text(rel.get("answer", ""))
                ans_tokens = ans.split()
                
                subj_present = has_word(subj, norm_transcript) if subj else False
                ans_present = any(has_word(tok, norm_transcript) for tok in ans_tokens)

                if subj_present and ans_present:
                    matched_relations.append(rel)
                elif subj_present and not ans_present:
                    failed_relations.append(rel)
                elif not subj_present and ans_present:
                    matched_relations.append(rel)

            if matched_relations and not failed_relations:
                return {
                    "concept_result": "correct",
                    "matched_concepts": [f"{r.get('subject', '')}_{r.get('answer', '')}" for r in matched_relations],
                    "missing_concepts": [],
                    "contradictions": [],
                    "match_tier": "relation_triplet"
                }
            elif matched_relations and failed_relations:
                return {
                    "concept_result": "partial",
                    "matched_concepts": [f"{r.get('subject', '')}_{r.get('answer', '')}" for r in matched_relations],
                    "missing_concepts": [f"{r.get('subject', '')}_{r.get('answer', '')}" for r in failed_relations],
                    "contradictions": [],
                    "match_tier": "partial_relations"
                }
            elif failed_relations:
                return {
                    "concept_result": "incorrect",
                    "matched_concepts": [],
                    "missing_concepts": [f"{r.get('subject', '')}_{r.get('answer', '')}" for r in failed_relations],
                    "contradictions": [],
                    "match_tier": "failed_relations"
                }

        # ----------------------------------------------------

        # Tier 5: Expected Concepts Semantic Match
        # ----------------------------------------------------
        matched_c = []
        missing_c = []
        for c in expected_concepts:
            norm_c = normalize_text(c)
            # Check key content words (ignore stop words like in, on, the, a, to)
            stop_words = {"in", "on", "the", "a", "an", "to", "its", "at", "is", "are"}
            c_keywords = [w for w in norm_c.split() if w not in stop_words]
            
            matches_count = sum(1 for kw in c_keywords if kw in norm_transcript)
            if matches_count >= max(1, len(c_keywords) // 2):
                matched_c.append(c)
            else:
                missing_c.append(c)

        if len(matched_c) == len(expected_concepts) and len(expected_concepts) > 0:
            return {
                "concept_result": "correct",
                "matched_concepts": matched_c,
                "missing_concepts": [],
                "contradictions": [],
                "match_tier": "expected_concepts"
            }
        elif len(matched_c) > 0:
            return {
                "concept_result": "partial",
                "matched_concepts": matched_c,
                "missing_concepts": missing_c,
                "contradictions": [],
                "match_tier": "partial_concepts"
            }

        return {
            "concept_result": "incorrect",
            "matched_concepts": [],
            "missing_concepts": expected_concepts,
            "contradictions": [],
            "match_tier": "none"
        }

answer_checker = AnswerChecker()
