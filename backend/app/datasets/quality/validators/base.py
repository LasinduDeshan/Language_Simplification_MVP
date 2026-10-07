"""Base abstract validator class for Stage 15 quality rules."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.datasets.quality.schemas import QualityRuleResultV1


class BaseValidator(ABC):
    """Abstract base class that all record and layer validators implement."""

    validator_name: str = "base_validator"
    validator_version: str = "1.0.0"

    @abstractmethod
    def validate(self, record: Dict[str, Any], run_id: str = "adhoc_run") -> List[QualityRuleResultV1]:
        """
        Executes rules against a single dictionary-serialized record or layer payload.
        Returns a list of QualityRuleResultV1 objects.
        """
        raise NotImplementedError
