"""Rights enforcement gate for external dataset processing."""

from typing import Tuple
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.schemas import ExternalDatasetId


class RightsGate:
    """Enforces legal rights and usage permissions before acquisition or processing."""

    def __init__(self, registry: ExternalDatasetRegistry):
        self.registry = registry

    def check_acquisition_allowed(self, dataset_id: ExternalDatasetId) -> Tuple[bool, str]:
        """Validates whether a dataset may be downloaded for local research."""
        record = self.registry.get(dataset_id)
        if not record:
            return False, f"Dataset {dataset_id} is not registered in the external dataset registry."
        if record.rights_status == "pending_content_rights_verification":
            return False, f"Dataset {dataset_id} has unverified content rights ('pending_content_rights_verification')."
        if record.rights_status == "excluded_rights":
            return False, f"Dataset {dataset_id} is excluded under rights policy ('excluded_rights')."
        if not record.permissions.local_processing_allowed:
            return False, f"Dataset {dataset_id} lacks 'local_processing_allowed' permission."
        return True, f"Dataset {dataset_id} is approved for local research processing."

    def check_benchmark_allowed(self, dataset_id: ExternalDatasetId) -> Tuple[bool, str]:
        """Validates whether a dataset may be used as an evaluation benchmark."""
        allowed, reason = self.check_acquisition_allowed(dataset_id)
        if not allowed:
            return False, reason
        record = self.registry.get(dataset_id)
        if not record.permissions.benchmark_use_allowed:
            return False, f"Dataset {dataset_id} does not permit benchmark evaluation use."
        return True, f"Dataset {dataset_id} is approved for benchmark evaluation."

    def check_training_allowed(self, dataset_id: ExternalDatasetId) -> Tuple[bool, str]:
        """Validates whether a dataset may produce training candidates."""
        allowed, reason = self.check_acquisition_allowed(dataset_id)
        if not allowed:
            return False, reason
        record = self.registry.get(dataset_id)
        if not record.permissions.training_use_allowed:
            return False, f"Dataset {dataset_id} does not permit training candidate derivation."
        return True, f"Dataset {dataset_id} is approved for training candidate derivation."
