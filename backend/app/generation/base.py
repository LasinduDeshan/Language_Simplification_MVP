from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from app.database.models import Task, LearnerProfile, Attempt

class BaseInstructionGenerator(ABC):
    """
    Abstract Base Class for Child-Friendly Adaptive Instruction Generators.
    Ensures consistent output structure across Rule-based, LLM, and Hybrid generators.
    """

    @abstractmethod
    def generate(
        self,
        task: Task,
        learner: LearnerProfile,
        target_attempt_number: int,
        support_level: str,
        previous_attempt: Optional[Attempt] = None,
        previous_observations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generates child-friendly instruction payload:
        {
            "child_instruction": str,       # Target <= 8-10 words, strict max 12 words
            "supportive_message": str,      # Warm encouraging non-punitive prompt
            "vocabulary_support": list,     # Word replacements with simple definitions
            "answer_format": str,           # Interaction modality (speech, two_picture_choice, etc.)
            "visual_cues": list,            # List of visual cue tags
            "reason_codes": list,           # Explainable audit trail
            "generation_method": str        # rule, llm, or hybrid
        }
        """
        pass
