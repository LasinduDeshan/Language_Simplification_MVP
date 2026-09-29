"""Tests for RightsGate enforcement and permission checks."""

import pytest
from pathlib import Path
import tempfile
from app.datasets.external_english.registry import ExternalDatasetRegistry
from app.datasets.external_english.rights_gate import RightsGate
from app.datasets.external_english.schemas import (
    DatasetPermissions,
    ExternalDatasetRegistryRecord,
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


def test_rights_gate_benchmark_permission():
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = ExternalDatasetRegistry(registry_dir=Path(tmpdir))
        rec = ExternalDatasetRegistryRecord(
            dataset_id="EXTDATA-ASSET",
            dataset_name="ASSET",
            official_source_url="https://github.com/facebookresearch/asset",
            publication_reference="Alva-Manchego et al., ACL 2020",
            rights_status="approved_local_research",
            permissions=DatasetPermissions(local_processing_allowed=True, benchmark_use_allowed=True, training_use_allowed=False),
        )
        registry.register(rec)
        gate = RightsGate(registry=registry)

        # Benchmark allowed
        allowed, reason = gate.check_benchmark_allowed("EXTDATA-ASSET")
        assert allowed is True

        # Training candidate rejected due to benchmark-only restriction
        allowed_train, reason_train = gate.check_training_allowed("EXTDATA-ASSET")
        assert allowed_train is False
        assert "does not permit training" in reason_train
