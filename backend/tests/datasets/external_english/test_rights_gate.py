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

        allowed, reason = gate.authorize("EXTDATA-ASSET", action="acquire")
        assert allowed is False
        assert "not registered" in reason


def test_rights_gate_pending_verification():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-TURKCORPUS",
            dataset_name="TurkCorpus",
            official_source_url="https://github.com/cocoxu/simplification",
            publication_reference="Xu et al., TACL 2016",
            rights_status="pending_content_rights_verification",
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        allowed, reason = gate.authorize("EXTDATA-TURKCORPUS", action="acquire")
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

        allowed, reason = gate.authorize("EXTDATA-NEWSELA", action="acquire")
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


def test_rights_gate_action_authorization():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        valid_evidence = RightsEvidence(
            evidence_type="dataset_license_file",
            evidence_url="https://raw.githubusercontent.com/facebookresearch/asset/9d659040d0d8942dbc4cd65cf357563b43fd9ab4/LICENSE",
            commit_sha="9d659040d0d8942dbc4cd65cf357563b43fd9ab4",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            verified_licence_identifier="CC-BY-NC-4.0",
            permission_rationale="Verified primary commit-pinned repository LICENSE file (CC-BY-NC 4.0) covers dataset content.",
            verified_by="research_governance_lead",
            intended_use_context="noncommercial_academic_research",
            commercial_use_allowed=False,
            requires_attribution=True,
            noncommercial_only=True,
        )
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(
                local_processing_allowed=True,
                redistribution_allowed=False,
                benchmark_use_allowed=True,
                training_use_allowed=False,
                derived_feature_release_allowed=True,
            ),
            evidence=valid_evidence,
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        # 1. Acquire allowed
        allowed, _ = gate.authorize("EXTDATA-ASSET", action="acquire")
        assert allowed is True

        # 2. Local process allowed
        allowed, _ = gate.authorize("EXTDATA-ASSET", action="local_process")
        assert allowed is True

        # 3. Benchmark evaluation allowed
        allowed, _ = gate.authorize("EXTDATA-ASSET", action="benchmark")
        assert allowed is True

        # 4. Training candidate derivation denied
        allowed, reason = gate.authorize("EXTDATA-ASSET", action="train")
        assert allowed is False
        assert "training_use_allowed" in reason

        # 5. Raw and normalized redistribution denied under current registry
        allowed_raw, reason_raw = gate.authorize("EXTDATA-ASSET", action="redistribute_raw")
        assert allowed_raw is False
        assert "redistribution_allowed" in reason_raw

        allowed_norm, reason_norm = gate.authorize("EXTDATA-ASSET", action="redistribute_normalized")
        assert allowed_norm is False
        assert "redistribution_allowed" in reason_norm

        # 6. Feature release allowed
        allowed_feat, _ = gate.authorize("EXTDATA-ASSET", action="release_features")
        assert allowed_feat is True


def test_rights_gate_commercial_use_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        evidence = RightsEvidence(
            evidence_type="dataset_license_file",
            evidence_url="https://raw.githubusercontent.com/facebookresearch/asset/9d659040d0d8942dbc4cd65cf357563b43fd9ab4/LICENSE",
            commit_sha="9d659040d0d8942dbc4cd65cf357563b43fd9ab4",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            verified_licence_identifier="CC-BY-NC-4.0",
            permission_rationale="Verified primary license file (CC-BY-NC 4.0).",
            verified_by="research_governance_lead",
            noncommercial_only=True,
        )
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(local_processing_allowed=True, benchmark_use_allowed=True),
            evidence=evidence,
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        # Commercial context rejected
        allowed, reason = gate.authorize("EXTDATA-ASSET", action="benchmark", use_context="commercial_deployment")
        assert allowed is False
        assert "restricted to non-commercial academic research" in reason

        # Unspecified context rejected
        allowed_unspec, reason_unspec = gate.authorize("EXTDATA-ASSET", action="benchmark", use_context="unspecified")
        assert allowed_unspec is False
        assert "restricted to non-commercial academic research" in reason_unspec


def test_release_respects_redistribution_permissions():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        evidence = RightsEvidence(
            evidence_type="dataset_license_file",
            evidence_url="https://raw.githubusercontent.com/facebookresearch/asset/9d659040d0d8942dbc4cd65cf357563b43fd9ab4/LICENSE",
            commit_sha="9d659040d0d8942dbc4cd65cf357563b43fd9ab4",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            verified_licence_identifier="CC-BY-NC-4.0",
            permission_rationale="Verified CC-BY-NC 4.0 license.",
            verified_by="research_governance_lead",
            noncommercial_only=True,
        )
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(
                local_processing_allowed=True,
                redistribution_allowed=False,  # Prohibits text redistribution
                benchmark_use_allowed=True,
                derived_feature_release_allowed=True,
            ),
            evidence=evidence,
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        # Invariant: redistribution_allowed=False must forbid raw and normalized text redistribution
        can_redistribute_raw, _ = gate.authorize("EXTDATA-ASSET", action="redistribute_raw")
        can_redistribute_norm, _ = gate.authorize("EXTDATA-ASSET", action="redistribute_normalized")
        can_release_features, _ = gate.authorize("EXTDATA-ASSET", action="release_features")

        assert can_redistribute_raw is False
        assert can_redistribute_norm is False
        assert can_release_features is True
