"""
Stage 29 Manifest Generator
Generates docs/stage29_manifest.sha256 for all 11 controlled documentation artifacts.
"""

import sys
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"

ARTIFACTS = [
    "stage29_implementation_plan.md",
    "stage29_unicode_storage_audit.md",
    "stage29_locale_contract.md",
    "stage29_database_migration_or_no_change_report.md",
    "stage29_font_and_licence_record.md",
    "stage29_api_round_trip_report.md",
    "stage29_ui_rendering_report.md",
    "stage29_accessibility_report.md",
    "stage29_accounting_summary.md",
    "stage29_reproducibility_record.json",
    "stage29_completion_record.md"
]

def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    manifest_path = DOCS_DIR / "stage29_manifest.sha256"
    lines = []
    print("[Manifest Generator] Computing SHA-256 for Stage 29 controlled documentation artifacts:")
    for fname in ARTIFACTS:
        fpath = DOCS_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Missing required artifact: {fpath}")
        sha = compute_file_sha256(fpath)
        print(f"  {sha}  docs/{fname}")
        lines.append(f"{sha}  docs/{fname}")
    
    content = "\n".join(lines) + "\n"
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"[Manifest Generator] Successfully wrote {manifest_path}")

if __name__ == "__main__":
    generate_manifest()
