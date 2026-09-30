"""Builder for External English Dataset Non-Reconstructable Release 0.1.0."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.datasets.external_english.benchmark.metrics import estimate_fkgl, tokenize_words
from app.datasets.external_english.schemas import NormalizedExternalRecord


class ExternalReleaseBuilder:
    """Constructs release artifacts containing strictly non-reconstructable metadata and metrics."""

    RELEASE_VERSION = "0.1.0"

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is not None:
            self.output_dir = Path(output_dir)
        else:
            default_path = Path("data/external_english/releases/0.1.0")
            if default_path.exists():
                self.output_dir = default_path
            else:
                current = Path(__file__).resolve().parent
                found = None
                for parent in [current, *current.parents]:
                    if (parent / "data").exists():
                        found = parent
                        break
                self.output_dir = (found / "data" / "external_english" / "releases" / "0.1.0") if found else default_path

    def build_release(
        self,
        records: List[NormalizedExternalRecord],
        evaluation_results: Dict[str, Any],
        leakage_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Serializes release files and produces cryptographic manifest."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Non-reconstructable record metadata (JSONL)
        metadata_records = []
        for r in records:
            src_words = len(tokenize_words(r.evaluation_source_text))
            src_chars = len(r.evaluation_source_text)
            src_fkgl = estimate_fkgl(r.evaluation_source_text)

            ref_word_counts = [len(tokenize_words(ref)) for ref in r.evaluation_references]
            ref_char_counts = [len(ref) for ref in r.evaluation_references]
            ref_fkgls = [estimate_fkgl(ref) for ref in r.evaluation_references]

            non_reconstructable_entry = {
                "external_record_id": r.external_record_id,
                "dataset_id": r.dataset_id,
                "dataset_record_id": r.dataset_record_id,
                "source_group_id": r.source_group_id,
                "original_source_split": r.original_source_split,
                "reference_count": r.reference_count,
                "content_hash": r.content_hash,
                "quality_disposition": r.quality_disposition,
                "age_domain_status": r.age_domain_status,
                "final_disposition": r.final_disposition,
                "evaluation_protected": r.evaluation_protected,
                "training_eligible": r.training_eligible,
                "benchmark_eligible": r.benchmark_eligible,
                "approved_for_child_delivery": r.approved_for_child_delivery,
                "numerical_features": {
                    "source_char_length": src_chars,
                    "source_word_count": src_words,
                    "source_fkgl": round(src_fkgl, 2),
                    "mean_ref_char_length": round(sum(ref_char_counts) / len(ref_char_counts), 2),
                    "mean_ref_word_count": round(sum(ref_word_counts) / len(ref_word_counts), 2),
                    "mean_ref_fkgl": round(sum(ref_fkgls) / len(ref_fkgls), 2),
                },
                "provenance": r.provenance,
            }
            metadata_records.append(non_reconstructable_entry)

        metadata_file = self.output_dir / "record_metadata.jsonl"
        with open(metadata_file, "w", encoding="utf-8") as f:
            for entry in metadata_records:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # 2. Benchmark only IDs list
        benchmark_ids_file = self.output_dir / "benchmark_only_ids.json"
        benchmark_ids = [r.external_record_id for r in records if r.final_disposition == "benchmark_only"]
        with open(benchmark_ids_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "release_version": self.RELEASE_VERSION,
                    "total_benchmark_ids": len(benchmark_ids),
                    "ids": benchmark_ids,
                },
                f,
                indent=2,
            )

        # 3. Aggregate Dataset Statistics
        stats_file = self.output_dir / "dataset_statistics.json"
        val_records = [r for r in records if r.original_source_split == "validation"]
        test_records = [r for r in records if r.original_source_split == "test"]
        stats = {
            "release_version": self.RELEASE_VERSION,
            "dataset_id": "EXTDATA-ASSET",
            "total_source_groups": len(records),
            "total_reference_instances": sum(r.reference_count for r in records),
            "splits": {
                "validation": {
                    "source_groups": len(val_records),
                    "reference_instances": sum(r.reference_count for r in val_records),
                    "references_per_source": 10,
                },
                "test": {
                    "source_groups": len(test_records),
                    "reference_instances": sum(r.reference_count for r in test_records),
                    "references_per_source": 10,
                },
            },
            "leakage_statistics": {
                "exact_overlaps": leakage_summary.get("exact_overlap_count", 0),
                "near_overlaps": leakage_summary.get("near_overlap_count", 0),
                "status": leakage_summary.get("leakage_status", "CLEAN"),
            },
            "governance_locks": {
                "evaluation_protected": True,
                "training_eligible": False,
                "benchmark_eligible": True,
                "approved_for_child_delivery": False,
            },
        }
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        # 4. Benchmark Evaluation Results
        eval_file = self.output_dir / "benchmark_evaluation_results.json"
        with open(eval_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "release_version": self.RELEASE_VERSION,
                    "evaluation_suite": "Stage 23 ASSET Baseline Evaluation",
                    "results": evaluation_results,
                },
                f,
                indent=2,
            )

        # 5. Cryptographic SHA-256 Manifest
        release_files = [
            metadata_file,
            benchmark_ids_file,
            stats_file,
            eval_file,
        ]
        manifest_lines = []
        for rf in release_files:
            hasher = hashlib.sha256()
            with open(rf, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            manifest_lines.append(f"{file_hash}  {rf.name}")

        manifest_file = self.output_dir / "release_manifest.sha256"
        with open(manifest_file, "w", encoding="utf-8") as f:
            f.write("\n".join(manifest_lines) + "\n")

        return {
            "release_dir": str(self.output_dir),
            "files_generated": [str(rf) for rf in release_files] + [str(manifest_file)],
            "manifest_file": str(manifest_file),
            "total_records": len(records),
        }
