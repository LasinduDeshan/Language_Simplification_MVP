"""Adapter for the ASSET dataset (Alva-Manchego et al., ACL 2020)."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.datasets.external_english.normalization import process_dual_text_representation
from app.datasets.external_english.schemas import (
    ExternalDatasetId,
    FinalDispositionType,
    NormalizedExternalRecord,
)


class ASSETAdapter:
    """Ingests and converts official ASSET files into canonical NormalizedExternalRecord objects."""

    DATASET_ID: ExternalDatasetId = "EXTDATA-ASSET"
    EXPECTED_VAL_COUNT = 2000
    EXPECTED_TEST_COUNT = 359
    REFERENCE_COUNT = 10

    def __init__(self, raw_dir: Optional[Path] = None):
        if raw_dir is not None:
            self.raw_dir = Path(raw_dir)
        else:
            default_path = Path("data/external_english/asset/raw")
            if default_path.exists():
                self.raw_dir = default_path
            else:
                # Traverse up to find repo root containing data directory
                current = Path(__file__).resolve().parent
                repo_root = None
                for parent in [current, *current.parents]:
                    if (parent / "data" / "external_english" / "asset" / "raw").exists():
                        repo_root = parent
                        break
                if repo_root is not None:
                    self.raw_dir = repo_root / "data" / "external_english" / "asset" / "raw"
                else:
                    self.raw_dir = Path("data/external_english/asset/raw")

    def _load_split_files(
        self, split: str, expected_count: int
    ) -> Tuple[List[str], List[List[str]]]:
        """Loads source sentences and 10 reference files for a given split."""
        orig_file = self.raw_dir / f"asset.{split}.orig"
        if not orig_file.exists():
            raise FileNotFoundError(f"Missing ASSET source file: {orig_file}")

        with open(orig_file, "r", encoding="utf-8") as f:
            sources = [line.rstrip("\r\n") for line in f]

        if len(sources) != expected_count:
            raise ValueError(
                f"ASSET {split} sources count mismatch: expected {expected_count}, got {len(sources)}"
            )

        ref_matrix: List[List[str]] = []
        for ref_idx in range(self.REFERENCE_COUNT):
            ref_file = self.raw_dir / f"asset.{split}.simp.{ref_idx}"
            if not ref_file.exists():
                raise FileNotFoundError(f"Missing ASSET reference file: {ref_file}")
            with open(ref_file, "r", encoding="utf-8") as f:
                ref_lines = [line.rstrip("\r\n") for line in f]
            if len(ref_lines) != expected_count:
                raise ValueError(
                    f"ASSET {split} ref {ref_idx} count mismatch: expected {expected_count}, got {len(ref_lines)}"
                )
            ref_matrix.append(ref_lines)

        # Transpose to get 10 references per source group
        grouped_refs = []
        for row_idx in range(expected_count):
            grouped_refs.append([ref_matrix[r][row_idx] for r in range(self.REFERENCE_COUNT)])

        return sources, grouped_refs

    def load_validation_records(self) -> List[NormalizedExternalRecord]:
        """Loads and normalizes 2,000 validation source groups (20,000 reference instances)."""
        sources, grouped_refs = self._load_split_files("valid", self.EXPECTED_VAL_COUNT)
        records: List[NormalizedExternalRecord] = []

        for idx, (raw_src, raw_refs) in enumerate(zip(sources, grouped_refs), start=1):
            eval_src, eval_refs, content_hash = process_dual_text_representation(
                raw_src, raw_refs
            )
            rec = NormalizedExternalRecord(
                external_record_id=f"EXTREC-ASSET-VAL-{idx:04d}",
                schema_version="1.0.0",
                dataset_id=self.DATASET_ID,
                dataset_record_id=f"asset.valid.{idx:04d}",
                source_group_id=f"ASSET-VAL-{idx:04d}",
                raw_source_text=raw_src,
                raw_references=raw_refs,
                evaluation_source_text=eval_src,
                evaluation_references=eval_refs,
                raw_text_preserved=True,
                evaluation_view_derived=True,
                normalization_operations=[
                    "nfc_unicode_normalization",
                    "whitespace_normalization",
                ],
                official_benchmark_files_overwritten=False,
                reference_count=len(raw_refs),
                language="en",
                source_domain="wikipedia_general",
                original_source_split="validation",
                content_hash=content_hash,
                preprocessing_version="1.0.0",
                quality_disposition="passed",
                age_domain_status="general_domain_benchmark",
                evaluation_protected=True,
                protection_reason="external_benchmark_source",
                expert_dld_validated=False,
                approved_for_child_delivery=False,
                research_eligible=False,
                training_eligible=False,
                benchmark_eligible=True,
                final_disposition="benchmark_only",
                provenance={
                    "origin_split": "validation",
                    "line_index": idx,
                    "publication": "Alva-Manchego et al., ACL 2020",
                    "source_url": "https://github.com/facebookresearch/asset",
                },
            )
            records.append(rec)
        return records

    def load_test_records(self) -> List[NormalizedExternalRecord]:
        """Loads and normalizes 359 test source groups (3,590 reference instances)."""
        sources, grouped_refs = self._load_split_files("test", self.EXPECTED_TEST_COUNT)
        records: List[NormalizedExternalRecord] = []

        for idx, (raw_src, raw_refs) in enumerate(zip(sources, grouped_refs), start=1):
            eval_src, eval_refs, content_hash = process_dual_text_representation(
                raw_src, raw_refs
            )
            rec = NormalizedExternalRecord(
                external_record_id=f"EXTREC-ASSET-TEST-{idx:04d}",
                schema_version="1.0.0",
                dataset_id=self.DATASET_ID,
                dataset_record_id=f"asset.test.{idx:04d}",
                source_group_id=f"ASSET-TEST-{idx:04d}",
                raw_source_text=raw_src,
                raw_references=raw_refs,
                evaluation_source_text=eval_src,
                evaluation_references=eval_refs,
                raw_text_preserved=True,
                evaluation_view_derived=True,
                normalization_operations=[
                    "nfc_unicode_normalization",
                    "whitespace_normalization",
                ],
                official_benchmark_files_overwritten=False,
                reference_count=len(raw_refs),
                language="en",
                source_domain="wikipedia_general",
                original_source_split="test",
                content_hash=content_hash,
                preprocessing_version="1.0.0",
                quality_disposition="passed",
                age_domain_status="general_domain_benchmark",
                evaluation_protected=True,
                protection_reason="external_benchmark_source",
                expert_dld_validated=False,
                approved_for_child_delivery=False,
                research_eligible=False,
                training_eligible=False,
                benchmark_eligible=True,
                final_disposition="benchmark_only",
                provenance={
                    "origin_split": "test",
                    "line_index": idx,
                    "publication": "Alva-Manchego et al., ACL 2020",
                    "source_url": "https://github.com/facebookresearch/asset",
                },
            )
            records.append(rec)
        return records

    def load_all_records(self) -> List[NormalizedExternalRecord]:
        """Loads and returns all 2,359 canonical ASSET source groups."""
        return self.load_validation_records() + self.load_test_records()
