from abc import ABC, abstractmethod
from typing import List, Optional
from app.integrations.component1.schemas import Component1ScreeningInputSchema

class Component1Interface(ABC):
    """
    Abstract interface for Component 1 screening data provider.
    """
    @abstractmethod
    def get_screening_profile(self, learner_id: str) -> Optional[Component1ScreeningInputSchema]:
        """Retrieve a screening profile snapshot for a learner."""
        pass

    @abstractmethod
    def list_screening_profiles(self) -> List[Component1ScreeningInputSchema]:
        """List all available screening profiles."""
        pass
