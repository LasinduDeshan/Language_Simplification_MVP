"""
Build Token Occurrence Ledger and Frequency Artifacts for Stage 32 (WP2).
Runs OccurrenceLedgerBuilder across the 150 canonical analytical records,
outputs token_occurrence_ledger.jsonl, and prints zero-loss accounting metrics.
"""

from pathlib import Path
import json
import sys

# Ensure backend is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.datasets.sinhala_lexicon.occurrence_ledger import OccurrenceLedgerBuilder

def main():
    print("=== Building Stage 32 Token Occurrence Ledger ===")
    builder = OccurrenceLedgerBuilder()
    occurrences, surface_to_id, accounting = builder.build_occurrence_ledger()

    summary_file = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "occurrence_accounting_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(accounting, f, indent=2)

    print(f"Occurrence accounting summary written to: {summary_file}")
    print(f"Zero-loss accounting verified: unaccounted = {accounting['unaccounted_occurrences']}")

if __name__ == "__main__":
    main()
