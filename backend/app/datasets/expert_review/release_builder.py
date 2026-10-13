"""Release 0.3.0 Builder with Hard Release 0.2.0 Immutability Guard.

Builds governed Release 0.3.0 of the Simplification Corpus and auxiliary datasets,
incorporating expert reviews, taxonomy classifications, adjudications, and revisions,
while strictly verifying that Release 0.2.0 files are byte-for-byte unchanged.
"""
import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.datasets.expert_review.schemas import (
    ReviewManifestItem,
    AdjudicationRecord,
    RevisionRecord,
    TaxonomyClass,
    FinalDisposition,
    InventoryAccounting,
)

# Known cryptographically frozen hashes for Release 0.2.0
RELEASE_0_2_0_FROZEN_HASHES = {
    "dataset_issue_register.json": "088c32298b2f8457b8181a7604114ff52cc0a6ea5aae80c25127c8a89417ac3c",
    "simplification_corpus.json": "2e45b69158ccca5a490926c98ff49d5e4f7255b0e2476ca951206a1ab546e22c",
    "splits/development_candidate_test.json": "9cb505c7ee94f6d427c74869764f917066fa155d9819830cb7362e4d4a4623c8",
    "splits/development_candidate_train.json": "a514423d9c2c2ac468b4cc2b605d05da0bb7affb13582986cffffbf02ad7ef84",
    "splits/development_candidate_validation.json": "8f6d228ad916ef1bf046b68358a58c6ecf2929da5be609f2ef8798f0ec77e1d9",
    "splits/locked_test_manifest.json": "eac99f97ada351e1f3c53a0021d4b9ece9720e6efaf6a13e51a582d9a588bb9b",
}


class ReleaseBuilder:
    """Constructs Release 0.3.0 and enforces cryptographic immutability of Release 0.2.0."""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.rel_0_2_0_dir = os.path.join(
            root_dir, "data", "simplification_corpus", "releases", "0.2.0"
        )
        self.rel_0_3_0_dir = os.path.join(
            root_dir, "data", "simplification_corpus", "releases", "0.3.0"
        )

    def verify_release_0_2_0_immutability(self) -> Dict[str, str]:
        """Calculates current SHA-256 hashes of all Release 0.2.0 files and verifies them against the frozen baseline."""
        if not os.path.exists(self.rel_0_2_0_dir):
            raise FileNotFoundError(f"Release 0.2.0 directory not found at {self.rel_0_2_0_dir}")

        current_hashes: Dict[str, str] = {}
        for rel_file, expected_hash in RELEASE_0_2_0_FROZEN_HASHES.items():
            file_path = os.path.join(self.rel_0_2_0_dir, *rel_file.split("/"))
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Missing Release 0.2.0 file: {rel_file}")

            with open(file_path, "rb") as fp:
                file_hash = hashlib.sha256(fp.read()).hexdigest()

            if file_hash != expected_hash:
                raise ValueError(
                    f"CRITICAL IMMUTABILITY VIOLATION: Release 0.2.0 file {rel_file} has hash {file_hash}, "
                    f"expected frozen baseline {expected_hash}!"
                )
            current_hashes[rel_file] = file_hash

        return current_hashes

    def build_release_0_3_0(
        self,
        manifest_items: List[ReviewManifestItem],
        adjudication_records: Dict[str, AdjudicationRecord],
        revisions: Dict[str, RevisionRecord],
        inventory_accounting: InventoryAccounting,
    ) -> Dict[str, Any]:
        """Builds Release 0.3.0 directory with governed reference records and auxiliary partitions."""
        # Hard immutability check first
        self.verify_release_0_2_0_immutability()

        os.makedirs(self.rel_0_3_0_dir, exist_ok=True)
        aux_dir = os.path.join(self.rel_0_3_0_dir, "auxiliary")
        os.makedirs(aux_dir, exist_ok=True)

        retained_simplifications = []
        auxiliary_records = {
            "instruction_modifications": [],
            "activity_format_changes": [],
            "question_adaptations": [],
            "response_scaffolding": [],
            "invalid_or_unusable": [],
        }

        # Classify and partition items
        for item in manifest_items:
            item_id = item.item_id
            adj = adjudication_records.get(item_id)
            rev = revisions.get(item_id)

            tax_class = adj.final_taxonomy_class if adj else TaxonomyClass.TEXT_SIMPLIFICATION
            disp = adj.final_disposition if adj else FinalDisposition.EXPERT_APPROVED
            target_text = rev.revised_text if rev else item.target_text

            record_entry = {
                "item_id": item.item_id,
                "source_group_id": item.source_group_id,
                "record_type": item.record_type.value,
                "text_stimulus": item.text_stimulus,
                "target_text": target_text,
                "support_level": item.support_level.value if item.support_level else None,
                "target_age_min": item.target_age_min,
                "target_age_max": item.target_age_max,
                "taxonomy_class": tax_class.value,
                "final_disposition": disp.value,
                "content_hash": hashlib.sha256(target_text.strip().encode("utf-8")).hexdigest(),
                "governance": {
                    "dataset_version": "0.3.0",
                    "schema_version": "1.0.0",
                    "expert_reviewed": True,
                    "eligible_for_stage28_evaluation": (
                        tax_class == TaxonomyClass.TEXT_SIMPLIFICATION
                        and disp in (FinalDisposition.EXPERT_APPROVED, FinalDisposition.APPROVED_WITH_REVISION)
                    ),
                    "approved_for_unsupervised_child_delivery": False,
                    "recommended_for_supervised_child_delivery_review": True,
                    "requires_professional_monitoring": True,
                },
            }

            if tax_class == TaxonomyClass.TEXT_SIMPLIFICATION:
                retained_simplifications.append(record_entry)
            elif tax_class == TaxonomyClass.INSTRUCTION_REPHRASING:
                auxiliary_records["instruction_modifications"].append(record_entry)
            elif tax_class == TaxonomyClass.ACTIVITY_FORMAT_TRANSFORMATION:
                auxiliary_records["activity_format_changes"].append(record_entry)
            elif tax_class == TaxonomyClass.QUESTION_GENERATION:
                auxiliary_records["question_adaptations"].append(record_entry)
            elif tax_class == TaxonomyClass.RESPONSE_MODE_ADAPTATION:
                auxiliary_records["response_scaffolding"].append(record_entry)
            elif tax_class == TaxonomyClass.INVALID_OR_UNUSABLE:
                auxiliary_records["invalid_or_unusable"].append(record_entry)

        # Write simplification_corpus.json
        corpus_path = os.path.join(self.rel_0_3_0_dir, "simplification_corpus.json")
        with open(corpus_path, "w", encoding="utf-8") as fp:
            json.dump({
                "schema_version": "1.0.0",
                "dataset_version": "0.3.0",
                "historical_reference_version": "0.2.0",
                "total_records": len(retained_simplifications),
                "records": retained_simplifications,
            }, fp, indent=2)

        # Write auxiliary corpora
        for category, aux_list in auxiliary_records.items():
            aux_file = os.path.join(aux_dir, f"{category}.json")
            with open(aux_file, "w", encoding="utf-8") as fp:
                json.dump({
                    "schema_version": "1.0.0",
                    "dataset_version": "0.3.0",
                    "category": category,
                    "total_records": len(aux_list),
                    "records": aux_list,
                }, fp, indent=2)

        # Write adjudication_records.jsonl
        adj_path = os.path.join(self.rel_0_3_0_dir, "adjudication_records.jsonl")
        with open(adj_path, "w", encoding="utf-8") as fp:
            for adj in adjudication_records.values():
                fp.write(adj.model_dump_json() + "\n")

        # Write revision_history.jsonl
        rev_path = os.path.join(self.rel_0_3_0_dir, "revision_history.jsonl")
        with open(rev_path, "w", encoding="utf-8") as fp:
            for rev in revisions.values():
                fp.write(rev.model_dump_json() + "\n")

        # Build release manifest
        manifest_meta = {
            "schema_version": "1.0.0",
            "release_version": "0.3.0",
            "built_at": datetime.utcnow().isoformat(),
            "predecessor_release": "0.2.0",
            "predecessor_immutability_verified": True,
            "benchmark_track_separation": {
                "historical_locked_benchmark": "historical_locked_release_0.2.0",
                "expert_reviewed_benchmark": "expert_reviewed_reference_release_0.3.0",
            },
            "inventory_accounting": inventory_accounting.model_dump(),
            "retained_simplification_records": len(retained_simplifications),
            "auxiliary_records_summary": {k: len(v) for k, v in auxiliary_records.items()},
        }

        manifest_path = os.path.join(self.rel_0_3_0_dir, "release_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as fp:
            json.dump(manifest_meta, fp, indent=2)

        # Generate sha256 checksums for 0.3.0 files
        checksums = {}
        for root, _, files in os.walk(self.rel_0_3_0_dir):
            for file in files:
                if file.endswith(".sha256"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.rel_0_3_0_dir).replace("\\", "/")
                with open(full_path, "rb") as fp:
                    checksums[rel_path] = hashlib.sha256(fp.read()).hexdigest()

        sha_path = os.path.join(self.rel_0_3_0_dir, "release_manifest.sha256")
        with open(sha_path, "w", encoding="utf-8") as fp:
            for fpath in sorted(checksums.keys()):
                fp.write(f"{checksums[fpath]}  {fpath}\n")

        return {
            "release_version": "0.3.0",
            "release_directory": self.rel_0_3_0_dir,
            "retained_simplifications": len(retained_simplifications),
            "total_auxiliary_records": sum(len(v) for v in auxiliary_records.values()),
            "checksums_generated": len(checksums),
        }
