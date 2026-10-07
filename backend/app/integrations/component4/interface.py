from abc import ABC, abstractmethod
from typing import Optional
from app.integrations.component4.schemas import Component4PerformanceExportSchema

class Component4Interface(ABC):
    """
    Abstract interface for Component 4 learning analytics exporter.
    """
    @abstractmethod
    def export_learner_performance(self, learner_id: str, db_session) -> Component4PerformanceExportSchema:
        """Generate and export performance records for a learner."""
        pass
