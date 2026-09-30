"""Rights enforcement gate for external dataset processing and action-level authorization."""

import re
from typing import Tuple
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.schemas import (
    ExternalDatasetAction,
    ExternalDatasetId,
    RightsEvidence,
)


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

    def authorize(
        self,
        dataset_id: ExternalDatasetId,
        action: ExternalDatasetAction,
        use_context: str = "noncommercial_academic_research",
    ) -> Tuple[bool, str]:
        """Authorizes or denies a specific requested action for a dataset within an intended use context."""
        record = self.registry.get(dataset_id)
        if not record:
            return False, f"Dataset {dataset_id} is not registered in the external dataset registry."
        if record.rights_status == "pending_content_rights_verification":
            return False, f"Dataset {dataset_id} has unverified content rights ('pending_content_rights_verification')."
        if record.rights_status == "pending_lineage_and_rights_verification":
            return False, f"Dataset {dataset_id} has unverified lineage/rights ('pending_lineage_and_rights_verification')."
        if record.rights_status == "excluded_rights":
            return False, f"Dataset {dataset_id} is excluded under rights policy ('excluded_rights')."

        # Check evidence for approved datasets
        if record.rights_status in ("approved_local_research", "approved_public_research"):
            valid_evidence, err = self.validate_approval_evidence(record.evidence)
            if not valid_evidence:
                return False, f"Approval gate failed for {dataset_id}: {err}"

        # Context evaluation (e.g. Noncommercial constraints)
        if record.evidence and record.evidence.noncommercial_only:
            if use_context != "noncommercial_academic_research":
                return False, f"Dataset {dataset_id} is restricted to non-commercial academic research (requested context: '{use_context}')."

        # Action-level permission check
        perms = record.permissions
        if action == "acquire":
            if not perms.local_processing_allowed:
                return False, f"Dataset {dataset_id} lacks 'local_processing_allowed' permission for acquisition."
            return True, f"Acquisition of {dataset_id} is authorized for local research."

        elif action == "local_process":
            if not perms.local_processing_allowed:
                return False, f"Dataset {dataset_id} lacks 'local_processing_allowed' permission."
            return True, f"Local processing of {dataset_id} is authorized."

        elif action == "benchmark":
            if not perms.benchmark_use_allowed:
                return False, f"Dataset {dataset_id} lacks 'benchmark_use_allowed' permission."
            return True, f"Benchmark evaluation using {dataset_id} is authorized."

        elif action == "train":
            if not perms.training_use_allowed:
                return False, f"Dataset {dataset_id} does not permit training candidate derivation ('training_use_allowed' is False)."
            return True, f"Training candidate derivation from {dataset_id} is authorized."

        elif action in ("redistribute_raw", "redistribute_normalized"):
            if not perms.redistribution_allowed:
                return False, f"Dataset {dataset_id} prohibits text redistribution ('redistribution_allowed' is False)."
            return True, f"Redistribution of {dataset_id} text is authorized."

        elif action == "release_features":
            if not perms.derived_feature_release_allowed:
                return False, f"Dataset {dataset_id} does not permit derived feature releases."
            return True, f"Derived feature summary release for {dataset_id} is authorized."

        return False, f"Unknown or unsupported action: {action}"

    def check_acquisition_allowed(self, dataset_id: ExternalDatasetId, use_context: str = "noncommercial_academic_research") -> Tuple[bool, str]:
        """Convenience wrapper for acquisition authorization."""
        return self.authorize(dataset_id, action="acquire", use_context=use_context)

    def check_benchmark_allowed(self, dataset_id: ExternalDatasetId, use_context: str = "noncommercial_academic_research") -> Tuple[bool, str]:
        """Convenience wrapper for benchmark evaluation authorization."""
        return self.authorize(dataset_id, action="benchmark", use_context=use_context)

    def check_training_allowed(self, dataset_id: ExternalDatasetId, use_context: str = "noncommercial_academic_research") -> Tuple[bool, str]:
        """Convenience wrapper for training derivation authorization."""
        return self.authorize(dataset_id, action="train", use_context=use_context)
