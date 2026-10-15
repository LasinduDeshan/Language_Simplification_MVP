"""
Execute WP9 Public Corpus Export with Rights Enforcement and Text Suppression.
Exports public_export_corpus.jsonl, suppressing text for PROTECTED_INTERNAL_ONLY records (SRC-SI-004).
"""

import json
import sys
from pathlib import Path

# Add backend and project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_external.export_service import build_public_export_record
from app.datasets.sinhala_external.schemas import PilotCorpusRecord
from app.datasets.sinhala_external.storage import storage_manager

CORPUS_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
EXPORT_FILE = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "public_export_corpus.jsonl"

def run():
    print("--- Starting Stage 31 Public Corpus Export (WP9) ---")
    lines = CORPUS_FILE.read_text(encoding="utf-8").splitlines()
    print(f"Loaded {len(lines)} pilot corpus records.")

    exported_records = []
    suppressed_count = 0
    permitted_count = 0

    for line in lines:
        c_rec = PilotCorpusRecord.model_validate_json(line)
        norm_text = storage_manager.read_raw_file(c_rec.normalized_text_storage_ref).decode("utf-8")
        
        exp = build_public_export_record(c_rec, norm_text)
        if exp is None:
            continue

        if exp["text"] is None:
            suppressed_count += 1
            assert "SRC-SI-004" in exp["all_contributing_sources"], f"Unexpected text suppression on {exp['record_id']}"
        else:
            permitted_count += 1
            assert "SRC-SI-004" not in exp["all_contributing_sources"], f"Leaked protected text on {exp['record_id']}"

        exported_records.append(exp)

    # Write public export file
    with open(EXPORT_FILE, "w", encoding="utf-8", newline="\n") as f:
        for r in exported_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(exported_records)} public export records to: {EXPORT_FILE}")
    print(f"  Public Permitted Records (with text):      {permitted_count}")
    print(f"  Protected Internal Records (text suppressed): {suppressed_count}")
    print("  Verification: Zero literal text leaked from SRC-SI-004 (PASSED)")

if __name__ == "__main__":
    run()
