"""
Generate cryptographic SHA-256 manifest for Stage 31 deliverables.
Writes hashes in standard sha256sum format to data/sinhala_external/manifests/stage31_manifest.sha256.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "manifests" / "stage31_manifest.sha256"

# Authoritative Stage 31 deliverable files
TARGET_FILES = [
    # Documentation (11 files)
    "docs/stage31_accounting_summary.md",
    "docs/stage31_acquisition_and_provenance_report.md",
    "docs/stage31_candidate_source_register.csv",
    "docs/stage31_completion_record.md",
    "docs/stage31_deduplication_and_contamination_report.md",
    "docs/stage31_governance_report.md",
    "docs/stage31_implementation_plan.md",
    "docs/stage31_licence_and_rights_report.md",
    "docs/stage31_preprocessing_integration_report.md",
    "docs/stage31_quality_and_exclusion_report.md",
    "docs/stage31_reproducibility_record.json",
    # Registry & Licence Snapshots (11 files)
    "data/sinhala_external/registry/candidate_sources.json",
    "data/sinhala_external/registry/approved_sources.json",
    "data/sinhala_external/registry/method_development_predeclaration.json",
    "data/sinhala_external/registry/stage31_configuration.json",
    "data/sinhala_external/registry/licence_snapshots/CC-BY-4.0.txt",
    "data/sinhala_external/registry/licence_snapshots/CC-BY-SA-3.0.txt",
    "data/sinhala_external/registry/licence_snapshots/CC-BY-SA-4.0.txt",
    "data/sinhala_external/registry/licence_snapshots/CommonCrawl-Terms-2020.txt",
    "data/sinhala_external/registry/licence_snapshots/Madura-Online-Terms.txt",
    "data/sinhala_external/registry/licence_snapshots/NewsLK-Government-Terms.txt",
    "data/sinhala_external/registry/licence_snapshots/UCSC-LTRL-Academic-Research-Terms.txt",
    # Receipts (5 files)
    "data/sinhala_external/receipts/RET-SI-001-001.json",
    "data/sinhala_external/receipts/RET-SI-002-001.json",
    "data/sinhala_external/receipts/RET-SI-003-001.json",
    "data/sinhala_external/receipts/RET-SI-004-001.json",
    "data/sinhala_external/receipts/RET-SI-008-001.json",
    # Manifest & Corpus Metadata
    "data/sinhala_external/manifests/raw_source_manifest.sha256",
    "data/sinhala_external/corpus/corpus_metadata.json"
]

def generate_manifest():
    lines = []
    print(f"Generating manifest for {len(TARGET_FILES)} Stage 31 deliverable files...")
    for rel_path in sorted(TARGET_FILES):
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            raise FileNotFoundError(f"Missing required deliverable: {p}")
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        clean_path = rel_path.replace("\\", "/")
        lines.append(f"{h}  {clean_path}")
        print(f"  {h[:16]}...  {clean_path}")

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_bytes("\n".join(lines).encode("utf-8") + b"\n")
    print(f"\nManifest successfully written to: {MANIFEST_FILE}")

if __name__ == "__main__":
    generate_manifest()
