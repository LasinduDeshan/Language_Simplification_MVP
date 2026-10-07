from abc import ABC, abstractmethod
from typing import Optional
from app.integrations.component2_ar.schemas import Component2AROutputSchema

class Component2ARInterface(ABC):
    """
    Abstract interface for Component 2 (AR) content delivery.
    """
    @abstractmethod
    def generate_ar_payload(
        self,
        task_code: str,
        instruction: str,
        support_level: str = "moderate",
        steps: Optional[list] = None,
        vocabulary_targets: Optional[list] = None
    ) -> Component2AROutputSchema:
        """Generate an AR-compatible instruction payload."""
        pass
