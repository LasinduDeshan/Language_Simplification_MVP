"""
Stage 33 — Manifest Generator.
Generates:
1. docs/stage33_manifest.sha256 (13 controlled documentation deliverables)
2. data/sinhala_simplification/manifests/stage33_implementation_manifest.sha256
Strictly self-excluding.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DOCS_MANIFEST = PROJECT_ROOT / "docs" / "stage33_manifest.sha256"
IMPLEMENTATION_MANIFEST = PROJECT_ROOT / "data" / "sinhala_simplification" / "manifests" / "stage33_implementation_manifest.sha256"

CONTROLLED_DOCS = [
    "docs/stage33_accounting_summary.md",
    "docs/stage33_candidate_selection_and_fallback.md",
    "docs/stage33_completion_record.md",
    "docs/stage33_development_evaluation_report.md",
    "docs/stage33_error_analysis.md",
    "docs/stage33_implementation_plan.md",
    "docs/stage33_lexical_and_phrase_rules.md",
    "docs/stage33_locked_evaluation_report.md",
    "docs/stage33_meaning_preservation_policy.md",
    "docs/stage33_reproducibility_record.json",
    "docs/stage33_rule_governance_and_scope.md",
    "docs/stage33_schema_and_trace_contract.md",
    "docs/stage33_sentence_and_syntactic_rules.md",
]

GOVERNED_IMPLEMENTATION_FILES = [
    "backend/app/sinhala_simplification/__init__.py",
    "backend/app/sinhala_simplification/candidate_filter.py",
    "backend/app/sinhala_simplification/candidate_ranker.py",
    "backend/app/sinhala_simplification/candidate_selector.py",
    "backend/app/sinhala_simplification/enums.py",
    "backend/app/sinhala_simplification/lexical_rules.py",
    "backend/app/sinhala_simplification/phrase_rules.py",
    "backend/app/sinhala_simplification/pipeline.py",
    "backend/app/sinhala_simplification/protected_spans.py",
    "backend/app/sinhala_simplification/rule_registry.py",
    "backend/app/sinhala_simplification/schemas.py",
    "backend/app/sinhala_simplification/sentence_splitter.py",
    "backend/app/sinhala_simplification/serialization.py",
    "backend/app/sinhala_simplification/storage.py",
    "backend/app/sinhala_simplification/syntactic_rules.py",
    "backend/app/sinhala_simplification/trace_builder.py",
    "data/sinhala_simplification/evaluation/locked_evaluation_record.json",
    "data/sinhala_simplification/evaluation/locked_test_metadata.jsonl",
    "data/sinhala_simplification/evaluation/public_summary.json",
    "data/sinhala_simplification/evaluation/validation_metadata.jsonl",
    "data/sinhala_simplification/ledgers/candidate_ledger.jsonl",
    "data/sinhala_simplification/ledgers/final_disposition_ledger.jsonl",
    "data/sinhala_simplification/ledgers/rule_attempt_ledger.jsonl",
    "data/sinhala_simplification/ledgers/transformation_trace_ledger.jsonl",
    "data/sinhala_simplification/registry/protected_span_policy.json",
    "data/sinhala_simplification/registry/ranking_precedence.json",
    "data/sinhala_simplification/registry/rule_registry_public.json",
    "data/sinhala_simplification/registry/stage33_configuration.json",
    "data/sinhala_simplification/snapshots/stage32_prerequisite_snapshot.json",
]


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_manifests():
    print("=== Generating Stage 33 Manifests ===")

    # 1. Documentation Manifest (13 files)
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
