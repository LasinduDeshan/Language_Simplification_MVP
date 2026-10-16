"""
Stage 34 — Documentation Manifest Generator (WP9)
Generates docs/stage34_manifest.sha256 covering exactly the 12 Stage 34 documents, excluding itself.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MANIFEST_FILE = DOCS_DIR / "stage34_manifest.sha256"

STAGE34_DOCS = [
    "stage34_implementation_plan.md",
    "stage34_ethics_privacy_and_reviewer_governance.md",
    "stage34_expert_panel_and_conflict_record.md",
    "stage34_annotation_rubric_and_codebook.md",
    "stage34_sampling_assignment_and_blinding_protocol.md",
    "stage34_reviewer_training_and_qualification_report.md",
    "stage34_agreement_analysis_report.md",
    "stage34_semantic_drift_and_error_analysis.md",
    "stage34_adjudication_and_rule_disposition_report.md",
    "stage34_accounting_summary.md",
    "stage34_reproducibility_record.json",
    "stage34_completion_record.md",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest():
    lines = []
    for doc_name in STAGE34_DOCS:
        doc_path = DOCS_DIR / doc_name
        assert doc_path.exists(), f"Missing required document: {doc_path}"
        digest = sha256_file(doc_path)
        lines.append(f"{digest}  docs/{doc_name}\n")

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"Generated {MANIFEST_FILE} with {len(lines)} documents.")


if __name__ == "__main__":
    generate_manifest()
