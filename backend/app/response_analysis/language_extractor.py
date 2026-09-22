from typing import List, Dict, Any, Optional
from app.tasks.repository import task_repository

class LanguageExtractor:
    def analyze_vocabulary_and_comprehension(
        self,
        transcript: str,
        task,
        learner_age: int = 6,
        concept_result: str = "correct"
    ) -> List[Dict[str, Any]]:
        """
        Detects vocabulary difficulties, unfamiliar words, and comprehension issues.
        """
        observations: List[Dict[str, Any]] = []
        t_lower = (transcript or "").lower()
        task_instruction = getattr(task, "original_instruction", "").lower()
        vocab_dict = task_repository.get_vocabulary_dictionary()

        # 1. Vocabulary difficulty checks (task targets & transcript)
        for entry in vocab_dict:
            word = entry["word"].lower()
            min_age = entry["minimum_age"]
            
            # If word is in task original instruction or child transcript and child is younger than minimum_age
            if (word in task_instruction or word in t_lower) and learner_age < min_age:
                observations.append({
                    "category": "vocabulary",
                    "observation_code": f"unfamiliar_{word}",
                    "evidence": word,
                    "confidence": 0.90,
                    "confirmed": True,
                    "child_visible": False,
                    "difficulty": entry["difficulty"],
                    "simple_alternative": entry["simple_alternative"],
                    "simple_definition": entry["simple_definition"]
                })

        # 2. Instruction following & Step dropoff analysis
        task_type = getattr(task, "task_type", "") or getattr(task, "category", "")
        task_code = getattr(task, "task_code", "")
        if task_type in ["classroom", "sequence", "sentence_and_instruction"] or task_code in ["TASK-ENG-001", "TASK-ENG-004", "TASK-ENG-010"]:
            # Check if learner completed only the first step
            if "crayons" in t_lower and "paper" not in t_lower and "bin" not in t_lower:
                observations.append({
                    "category": "instruction",
                    "observation_code": "difficulty_with_two_step_instruction",
                    "evidence": transcript,
                    "confidence": 0.85,
                    "confirmed": True,
                    "child_visible": False,
                    "suggested_adaptation": "split_into_one_step_turns"
                })

        # 3. Entity comprehension mismatch
        if task_type == "comprehension":
            if "mouse" in t_lower and "lion" not in t_lower and "leo" not in t_lower:
                observations.append({
                    "category": "comprehension",
                    "observation_code": "entity_confusion_secondary_character",
                    "evidence": "mouse",
                    "confidence": 0.88,
                    "confirmed": True,
                    "child_visible": False,
                    "suggested_adaptation": "two_picture_choice_with_target"
                })

        return observations

language_extractor = LanguageExtractor()
