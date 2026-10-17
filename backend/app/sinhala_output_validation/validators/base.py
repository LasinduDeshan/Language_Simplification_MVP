"""
Base validator interface for Stage 36 Sinhala Output Validation pipeline.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from app.sinhala_output_validation.schemas import CandidateEnvelope, ValidatorFinding


class BaseValidator(ABC):
    """
    Abstract base validator. All Stage 36 validators inherit from this class.
    """

    def __init__(self, validator_id: str, version: str = "1.0.0"):
        self.validator_id = validator_id
        self.version = version

    @abstractmethod
    def validate(
        self,
        source_text: str,
        candidate_text: str,
        envelope: CandidateEnvelope,
        context: Dict[str, Any],
    ) -> List[ValidatorFinding]:
        """
        Execute validation logic on source and candidate texts.
        Returns a list of ValidatorFinding instances.
        If no issues are found, returns an empty list.
        """
        pass
