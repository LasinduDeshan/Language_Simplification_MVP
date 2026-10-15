"""
Generate cryptographic SHA-256 manifests for Stage 31 deliverables:
1. docs/stage31_manifest.sha256 (Controls 11 documentation files; excludes itself)
2. data/sinhala_external/manifests/stage31_manifest.sha256 (Controls 29 expanded implementation & documentation artifacts; excludes itself)
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DOCS_MANIFEST_FILE = PROJECT_ROOT / "docs" / "stage31_manifest.sha256"
IMPLEMENTATION_MANIFEST_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "manifests" / "stage31_manifest.sha256"

# 11 Planned Documentation Files (excl. checksum manifest itself)
DOC_FILES = [
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
]

# 18 Additional Governed Implementation / Data Artifacts
DATA_FILES = [
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
    # Raw manifest & Corpus Metadata (2 files)
    "data/sinhala_external/manifests/raw_source_manifest.sha256",
    "data/sinhala_external/corpus/corpus_metadata.json"
]

ALL_FILES_29 = DOC_FILES + DATA_FILES

def generate_manifests():
    # 1. Generate docs/stage31_manifest.sha256
    print(f"Generating docs manifest for {len(DOC_FILES)} documentation files...")
    doc_lines = []
    for rel_path in sorted(DOC_FILES):
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            raise FileNotFoundError(f"Missing doc file: {p}")
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        clean_path = rel_path.replace("\\", "/")
        doc_lines.append(f"{h}  {clean_path}")
        print(f"  {h[:16]}...  {clean_path}")

    DOCS_MANIFEST_FILE.write_bytes("\n".join(doc_lines).encode("utf-8") + b"\n")
    print(f"Documentation manifest successfully written to: {DOCS_MANIFEST_FILE}\n")

    # 2. Generate data/sinhala_external/manifests/stage31_manifest.sha256 (29 files)
    print(f"Generating expanded implementation manifest for {len(ALL_FILES_29)} artifacts...")
    all_lines = []
    for rel_path in sorted(ALL_FILES_29):
        p = PROJECT_ROOT / rel_path
        if not p.exists():
            raise FileNotFoundError(f"Missing artifact: {p}")
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        clean_path = rel_path.replace("\\", "/")
        all_lines.append(f"{h}  {clean_path}")
        print(f"  {h[:16]}...  {clean_path}")

    IMPLEMENTATION_MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMPLEMENTATION_MANIFEST_FILE.write_bytes("\n".join(all_lines).encode("utf-8") + b"\n")
    print(f"Implementation manifest successfully written to: {IMPLEMENTATION_MANIFEST_FILE}\n")

if __name__ == "__main__":
    generate_manifests()
