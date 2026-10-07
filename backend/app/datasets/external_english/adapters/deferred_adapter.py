"""Adapters for blocked/deferred candidate datasets using synthetic fixtures."""

from typing import Any, Dict, List, Optional
from app.datasets.external_english.normalization import process_dual_text_representation
from app.datasets.external_english.schemas import (
    ExternalDatasetId,
    FinalDispositionType,
    NormalizedExternalRecord,
)


class SyntheticDeferredAdapter:
    """Demonstrates schema compatibility for deferred datasets using synthetic fixtures only."""

    def __init__(self, dataset_id: ExternalDatasetId, status_reason: str):
        self.dataset_id = dataset_id
        self.status_reason = status_reason

    def parse_synthetic_fixture(
        self,
        raw_source: str,
        raw_refs: List[str],
        source_idx: int,
        split: str = "validation",
    ) -> NormalizedExternalRecord:
        """Converts synthetic fixture data into canonical schema with explicit excluded_rights disposition."""
        eval_src, eval_refs, content_hash = process_dual_text_representation(
            raw_source, raw_refs
        )
        return NormalizedExternalRecord(
            external_record_id=f"EXTREC-SYNTH-{self.dataset_id}-{split}-{source_idx:04d}",
            schema_version="1.0.0",
            dataset_id=self.dataset_id,
            dataset_record_id=f"synth.{split}.{source_idx:04d}",
            source_group_id=f"SYNTH-{self.dataset_id}-{split}-{source_idx:04d}",
            raw_source_text=raw_source,
            raw_references=raw_refs,
            evaluation_source_text=eval_src,
            evaluation_references=eval_refs,
            raw_text_preserved=True,
            evaluation_view_derived=True,
            normalization_operations=["nfc_unicode_normalization", "whitespace_normalization"],
            official_benchmark_files_overwritten=False,
            reference_count=len(raw_refs),
            language="en",
            source_domain="synthetic_fixture",
            original_source_split=split,
            content_hash=content_hash,
            preprocessing_version="1.0.0",
            quality_disposition="passed",
            age_domain_status="not_verified",
            evaluation_protected=True,
            protection_reason=self.status_reason,
            expert_dld_validated=False,
            approved_for_child_delivery=False,
            research_eligible=False,
            training_eligible=False,
            benchmark_eligible=False,
            final_disposition="excluded_rights",
            provenance={
                "is_synthetic_fixture": True,
                "status_reason": self.status_reason,
            },
        )
