"""
Stage 30 Checksum Manifest Generator
Generates docs/stage30_manifest.sha256 for all 11 manifest-controlled documentation deliverables.
Manifest Accounting: 12 deliverables = 11 controlled artifacts + 1 checksum manifest.
"""

import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
MANIFEST_PATH = DOCS_DIR / "stage30_manifest.sha256"

ARTIFACTS = [
    "stage30_implementation_plan.md",
    "stage30_unicode_normalization_policy.md",
    "stage30_sinhala_character_inventory.csv",
    "stage30_tokenization_specification.md",
    "stage30_sentence_segmentation_specification.md",
    "stage30_quality_and_review_policy.md",
    "stage30_fixture_evaluation_report.md",
    "stage30_error_analysis.md",
    "stage30_accounting_summary.md",
    "stage30_reproducibility_record.json",
    "stage30_completion_record.md"
]

def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    lines = []
    print("Computing SHA-256 checksums for Stage 30 controlled artifacts:")
    for fname in ARTIFACTS:
        fpath = DOCS_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Required deliverable missing: {fpath}")
        sha = compute_file_sha256(fpath)
        rel_path = f"docs/{fname}"
        lines.append(f"{sha}  {rel_path}")
        print(f"  {sha}  {rel_path}")

    # Write manifest with newline
    manifest_content = "\n".join(lines) + "\n"
    with open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(manifest_content)

    print(f"\nManifest successfully written to: {MANIFEST_PATH}")
    print(f"Total controlled deliverables: {len(ARTIFACTS)}")
    print(f"Manifest SHA-256: {compute_file_sha256(MANIFEST_PATH)}")

if __name__ == "__main__":
    generate_manifest()
