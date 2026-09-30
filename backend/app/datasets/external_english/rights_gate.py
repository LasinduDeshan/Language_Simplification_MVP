"""Rights enforcement gate for external dataset processing."""

import re
from typing import Tuple
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.schemas import ExternalDatasetId, RightsEvidence


class RightsGate:
    """Enforces legal rights, licensing terms, and primary evidence completeness."""

    def __init__(self, registry: ExternalDatasetRegistry):
        self.registry = registry

    def validate_approval_evidence(self, evidence: RightsEvidence) -> Tuple[bool, str]:
        """Validates that primary evidence satisfies strict governance requirements for approved status."""
        if not evidence:
            return False, "Primary rights evidence is missing."
        if not evidence.evidence_url or not evidence.evidence_url.strip():
            return False, "Evidence URL is absent or empty."
        if not evidence.evidence_sha256 or not re.match(r"^[a-fA-F0-9]{64}$", evidence.evidence_sha256.strip()):
            return False, "Evidence SHA-256 hash is absent, empty, or invalid (must be 64 hex characters)."
        if evidence.evidence_scope != "dataset_content":
            return False, f"Evidence scope is '{evidence.evidence_scope}' but must be 'dataset_content' (repository software licenses do not cover dataset content)."
        if not evidence.permission_rationale or len(evidence.permission_rationale.strip()) < 10:
            return False, "Permission rationale is missing or insufficiently detailed."
        if not evidence.verified_by or not evidence.verified_by.strip():
            return False, "Reviewer identity ('verified_by') is missing from rights evidence."
        return True, "Rights evidence is valid and complete."

    def check_acquisition_allowed(self, dataset_id: ExternalDatasetId) -> Tuple[bool, str]:
        """Validates whether a dataset may be downloaded for local research."""
        record = self.registry.get(dataset_id)
        if not record:
            return False, f"Dataset {dataset_id} is not registered in the external dataset registry."
        if record.rights_status == "pending_content_rights_verification":
            return False, f"Dataset {dataset_id} has unverified content rights ('pending_content_rights_verification')."
        if record.rights_status == "pending_lineage_and_rights_verification":
            return False, f"Dataset {dataset_id} has unverified lineage/rights ('pending_lineage_and_rights_verification')."
        if record.rights_status == "excluded_rights":
            return False, f"Dataset {dataset_id} is excluded under rights policy ('excluded_rights')."
        
        # If marked as approved, enforce strict primary evidence validation
        if record.rights_status in ("approved_local_research", "approved_public_research"):
            valid_evidence, err = self.validate_approval_evidence(record.evidence)
            if not valid_evidence:
                return False, f"Approval gate failed for {dataset_id}: {err}"

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
