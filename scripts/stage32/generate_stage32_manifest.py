"""
Stage 32 Manifest Generator.
Generates:
1. docs/stage32_manifest.sha256 (12 controlled documentation deliverables)
2. data/sinhala_lexicon/manifests/stage32_implementation_manifest.sha256 (governed implementation & data artifacts)
Strictly self-excluding.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DOCS_MANIFEST = PROJECT_ROOT / "docs" / "stage32_manifest.sha256"
IMPLEMENTATION_MANIFEST = PROJECT_ROOT / "data" / "sinhala_lexicon" / "manifests" / "stage32_implementation_manifest.sha256"

CONTROLLED_DOCS = [
    "docs/stage32_accounting_summary.md",
    "docs/stage32_completion_record.md",
    "docs/stage32_corpus_and_frequency_protocol.md",
    "docs/stage32_error_analysis.md",
    "docs/stage32_expert_review_readiness.md",
    "docs/stage32_implementation_plan.md",
    "docs/stage32_lexicon_evaluation_report.md",
    "docs/stage32_lexicon_governance_and_schema.md",
    "docs/stage32_morphology_and_surface_form_policy.md",
    "docs/stage32_provisional_banding_protocol.md",
    "docs/stage32_reproducibility_record.json",
    "docs/stage32_rights_and_export_report.md"
]

GOVERNED_IMPLEMENTATION_FILES = [
    "data/sinhala_lexicon/registry/stage32_configuration.json",
    "data/sinhala_lexicon/snapshots/stage31_prerequisite_snapshot.json",
    "data/sinhala_lexicon/ledgers/corpus_identity_ledger.json",
    "data/sinhala_lexicon/ledgers/token_occurrence_ledger.jsonl",
    "data/sinhala_lexicon/ledgers/candidate_entry_ledger.jsonl",
    "data/sinhala_lexicon/ledgers/surface_form_mapping.jsonl",
    "data/sinhala_lexicon/ledgers/provenance_weight_ledger.jsonl",
    "data/sinhala_lexicon/ledgers/weighted_parity_diagnostic.json",
    "data/sinhala_lexicon/lexicon/draft_lexicon.jsonl",
    "data/sinhala_lexicon/lexicon/review_queue.jsonl",
    "data/sinhala_lexicon/lexicon/public_metadata_export.jsonl",
    "backend/app/datasets/sinhala_lexicon/__init__.py",
    "backend/app/datasets/sinhala_lexicon/enums.py",
    "backend/app/datasets/sinhala_lexicon/schemas.py",
    "backend/app/datasets/sinhala_lexicon/storage.py",
    "backend/app/datasets/sinhala_lexicon/corpus_bridge.py",
    "backend/app/datasets/sinhala_lexicon/candidate_extractor.py",
    "backend/app/datasets/sinhala_lexicon/occurrence_ledger.py",
    "backend/app/datasets/sinhala_lexicon/surface_form_grouper.py",
    "backend/app/datasets/sinhala_lexicon/morphology_analyzer.py",
    "backend/app/datasets/sinhala_lexicon/feature_builder.py",
    "backend/app/datasets/sinhala_lexicon/banding.py",
    "backend/app/datasets/sinhala_lexicon/quality_router.py",
    "backend/app/datasets/sinhala_lexicon/rights_resolver.py",
    "backend/app/datasets/sinhala_lexicon/review_service.py",
    "backend/app/datasets/sinhala_lexicon/export_service.py",
    "backend/app/datasets/sinhala_lexicon/parity_analyzer.py"
]

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_manifests():
    print("=== Generating Stage 32 Manifests ===")

    # 1. Documentation Manifest (12 files)
    doc_lines = []
    for rel_path in sorted(CONTROLLED_DOCS):
        fp = PROJECT_ROOT / rel_path
        assert fp.exists(), f"Missing controlled doc: {rel_path}"
        sha = compute_sha256(fp)
        doc_lines.append(f"{sha}  {rel_path.replace(chr(92), '/')}")

    DOCS_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    DOCS_MANIFEST.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")
    print(f"Documentation manifest generated at: {DOCS_MANIFEST} ({len(doc_lines)} entries)")

    # 2. Implementation Manifest
    impl_lines = []
    for rel_path in sorted(GOVERNED_IMPLEMENTATION_FILES):
        fp = PROJECT_ROOT / rel_path
        assert fp.exists(), f"Missing implementation file: {rel_path}"
        sha = compute_sha256(fp)
        impl_lines.append(f"{sha}  {rel_path.replace(chr(92), '/')}")

    IMPLEMENTATION_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    IMPLEMENTATION_MANIFEST.write_text("\n".join(impl_lines) + "\n", encoding="utf-8")
    print(f"Implementation manifest generated at: {IMPLEMENTATION_MANIFEST} ({len(impl_lines)} entries)")

if __name__ == "__main__":
    generate_manifests()
