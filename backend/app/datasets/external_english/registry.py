"""Registry manager for Stage 23 External English Datasets."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from app.datasets.external_english.schemas import (
    ExternalDatasetId,
    ExternalDatasetRegistryRecord,
    RightsDecision,
)


class ExternalDatasetRegistry:
    """Manages dataset source metadata and formal rights evaluations."""

    def __init__(self, registry_dir: Optional[Path] = None):
        self.registry_dir = registry_dir or Path("data/external_english/registry")
        self.registry_file = self.registry_dir / "external_dataset_registry.json"
        self.decisions_file = self.registry_dir / "rights_decisions.json"
        self._registry: Dict[ExternalDatasetId, ExternalDatasetRegistryRecord] = {}
        self._decisions: Dict[ExternalDatasetId, RightsDecision] = {}
        self.load()

    def load(self) -> None:
        """Loads registry and rights decisions from disk if present."""
        if self.registry_file.exists():
            with open(self.registry_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._registry = {
                    k: ExternalDatasetRegistryRecord.model_validate(v)
                    for k, v in data.items()
                }
        if self.decisions_file.exists():
            with open(self.decisions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._decisions = {
                    k: RightsDecision.model_validate(v)
                    for k, v in data.items()
                }

    def save(self) -> None:
        """Serializes registry and rights decisions to disk."""
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(
                {k: v.model_dump(mode="json") for k, v in self._registry.items()},
                f,
                indent=2,
            )
        with open(self.decisions_file, "w", encoding="utf-8") as f:
            json.dump(
                {k: v.model_dump(mode="json") for k, v in self._decisions.items()},
                f,
                indent=2,
            )

    def register(self, record: ExternalDatasetRegistryRecord) -> None:
        """Registers or updates a dataset record."""
        self._registry[record.dataset_id] = record

    def record_decision(self, decision: RightsDecision) -> None:
        """Records a formal rights decision and synchronizes the registry record."""
        self._decisions[decision.dataset_id] = decision
        if decision.dataset_id in self._registry:
            rec = self._registry[decision.dataset_id]
            rec.rights_status = decision.rights_status
            rec.permissions = decision.permissions
            rec.rights_verified_by = decision.verified_by
            rec.rights_verified_at = decision.verified_at
            rec.notes = decision.evidence_summary

    def get(self, dataset_id: ExternalDatasetId) -> Optional[ExternalDatasetRegistryRecord]:
        """Retrieves a dataset record by ID."""
        return self._registry.get(dataset_id)

    def get_decision(self, dataset_id: ExternalDatasetId) -> Optional[RightsDecision]:
        """Retrieves a formal rights decision by dataset ID."""
        return self._decisions.get(dataset_id)

    def list_all(self) -> List[ExternalDatasetRegistryRecord]:
        """Returns all registered dataset records."""
        return list(self._registry.values())
