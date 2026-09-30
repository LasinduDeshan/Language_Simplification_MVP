"""Tests for RightsGate enforcement, permission checks, and strict evidence validation."""

import pytest
from pathlib import Path
import tempfile
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.rights_gate import RightsGate
from app.datasets.external_english.schemas import (
    DatasetPermissions,
    ExternalDatasetRegistryRecord,
    RightsEvidence,
)


def test_rights_gate_unregistered():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        gate = RightsGate(registry=registry)

        allowed, reason = gate.check_acquisition_allowed("EXTDATA-ASSET")
        assert allowed is False
        assert "not registered" in reason


def test_rights_gate_pending_verification():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="pending_content_rights_verification",
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        allowed, reason = gate.check_acquisition_allowed("EXTDATA-ASSET")
        assert allowed is False
        assert "unverified content rights" in reason


def test_rights_gate_excluded():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-NEWSELA",
            dataset_name="Newsela",
            official_source_url="https://newsela.com/data/",
            publication_reference="Xu et al., 2015",
            rights_status="excluded_rights",
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        allowed, reason = gate.check_acquisition_allowed("EXTDATA-NEWSELA")
        assert allowed is False
        assert "excluded under rights policy" in reason


def test_rights_gate_strict_evidence_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        gate = RightsGate(registry=registry)

        # 1. Missing evidence URL
        invalid_evidence_no_url = RightsEvidence(
            evidence_url=None,
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            permission_rationale="Valid detailed permission rationale statement.",
            verified_by="test_reviewer",
        )
        valid, err = gate.validate_approval_evidence(invalid_evidence_no_url)
        assert valid is False
        assert "URL is absent" in err

        # 2. Missing/Invalid evidence SHA-256
        invalid_evidence_bad_hash = RightsEvidence(
            evidence_url="https://example.com/LICENSE",
            evidence_sha256="not_a_valid_64_hex_hash",
            evidence_scope="dataset_content",
            permission_rationale="Valid detailed permission rationale statement.",
            verified_by="test_reviewer",
        )
        valid, err = gate.validate_approval_evidence(invalid_evidence_bad_hash)
        assert valid is False
        assert "SHA-256 hash" in err

        # 3. Software license scope cannot approve dataset content
        invalid_evidence_software_scope = RightsEvidence(
            evidence_url="https://example.com/LICENSE",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="repository_software",
            permission_rationale="Valid detailed permission rationale statement.",
            verified_by="test_reviewer",
        )
        valid, err = gate.validate_approval_evidence(invalid_evidence_software_scope)
        assert valid is False
        assert "repository software" in err

        # 4. Empty permission rationale
        invalid_evidence_empty_rationale = RightsEvidence(
            evidence_url="https://example.com/LICENSE",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            permission_rationale="",
            verified_by="test_reviewer",
        )
        valid, err = gate.validate_approval_evidence(invalid_evidence_empty_rationale)
        assert valid is False
        assert "rationale is missing" in err


def test_rights_gate_approved_with_valid_evidence():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        valid_evidence = RightsEvidence(
            evidence_type="dataset_license_file",
            evidence_url="https://raw.githubusercontent.com/facebookresearch/asset/master/LICENSE",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            verified_licence_identifier="CC-BY-NC-4.0",
            permission_rationale="Verified primary repository LICENSE file (CC-BY-NC 4.0) covers dataset content.",
            verified_by="research_governance_lead",
            requires_attribution=True,
            noncommercial_only=True,
        )
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(local_processing_allowed=True, benchmark_use_allowed=True, training_use_allowed=False),
            evidence=valid_evidence,
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        allowed, reason = gate.check_acquisition_allowed("EXTDATA-ASSET")
        assert allowed is True

        allowed_bench, reason_bench = gate.check_benchmark_allowed("EXTDATA-ASSET")
        assert allowed_bench is True

        allowed_train, reason_train = gate.check_training_allowed("EXTDATA-ASSET")
        assert allowed_train is False
        assert "does not permit training" in reason_train
