"""Tests for ExternalDatasetRegistry schema, loading, and serialization."""

import pytest
from pathlib import Path
import tempfile
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.schemas import (
    DatasetPermissions,
    ExternalDatasetRegistryRecord,
    RightsDecision,
    RightsEvidence,
)


def test_registry_serialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg_dir = Path(tmpdir)
        registry = ExternalDatasetRegistry(registry_dir=reg_dir)

        evidence = RightsEvidence(
            evidence_type="dataset_license_file",
            evidence_url="https://raw.githubusercontent.com/facebookresearch/asset/master/LICENSE",
            evidence_sha256="50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447",
            evidence_scope="dataset_content",
            verified_licence_identifier="CC-BY-NC-4.0",
            permission_rationale="Verified primary license file covers dataset content under CC-BY-NC 4.0.",
            verified_by="test_reviewer",
        )

        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            content_licence_name="CC-BY-NC 4.0",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(local_processing_allowed=True, benchmark_use_allowed=True),
            evidence=evidence,
        )
        registry.register(rec)
        registry.save()

        # Reload in new instance
        reloaded = ExternalDatasetRegistry(registry_dir=reg_dir)
        loaded_rec = reloaded.get("EXTDATA-ASSET")
        assert loaded_rec is not None
        assert loaded_rec.dataset_name == "ASSET"
        assert loaded_rec.permissions.local_processing_allowed is True
        assert loaded_rec.permissions.training_use_allowed is False
        assert loaded_rec.evidence is not None
        assert loaded_rec.evidence.evidence_sha256 == "50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447"


def test_registry_records_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg_dir = Path(tmpdir)
        registry = ExternalDatasetRegistry(registry_dir=reg_dir)

        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-TURKCORPUS",
            dataset_name="TurkCorpus",
            official_source_url="https://github.com/cocoxu/simplification",
            publication_reference="Xu et al., TACL 2016",
        )
        registry.register(rec)

        decision = RightsDecision(
            dataset_id="EXTDATA-TURKCORPUS",
            rights_status="pending_content_rights_verification",
            permissions=DatasetPermissions(),
            evidence_summary="Content rights pending: repository software license (GPL-3.0) does not cover dataset content.",
            verified_by="test_reviewer",
            verified_at="2026-09-29T16:00:00Z",
        )
        registry.record_decision(decision)

        retrieved = registry.get("EXTDATA-TURKCORPUS")
        assert retrieved.rights_status == "pending_content_rights_verification"
        assert retrieved.permissions.benchmark_use_allowed is False
