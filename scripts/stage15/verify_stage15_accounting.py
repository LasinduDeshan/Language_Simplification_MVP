"""Verifies Stage 15 record-count reconciliation and accounting invariants."""
import os
import sys
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from app.database.db import SessionLocal
from app.datasets.quality.models import ValidationRun, RecordQualitySummary


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    # Read public summary report
    pub_json_path = os.path.join(repo_root, "data", "quality_reports", "stage15", "public", "stage15_quality_report.json")
    if not os.path.exists(pub_json_path):
        print(f"[!] Public report not found at '{pub_json_path}'. Run validation first.")
        sys.exit(1)

    with open(pub_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = data["total_records"]
    acc = data["accounting"]
    passed = acc["passed_count"]
    failed = acc["failed_count"]
    review = acc["review_required_count"]
    quarantined = acc["quarantined_count"]
    unaccounted = acc["unaccounted_count"]

    reconciled = passed + failed + review + quarantined

    print("==================================================================")
    print("STAGE 15 ACCOUNTING RECONCILIATION VERIFICATION")
    print("==================================================================")
    print(f"Total Source Records:          {total}")
    print(f"Passed Checks:                 {passed}")
    print(f"Failed Checks:                 {failed}")
    print(f"Manual Review Required:        {review}")
    print(f"Quarantined Records:           {quarantined}")
    print(f"Reconciled Sum:                {reconciled}")
    print(f"Unaccounted Count:             {unaccounted}")

    assert unaccounted == 0, f"Accounting mismatch: {unaccounted} records unaccounted for!"
    assert total == reconciled, f"Accounting discrepancy: total={total} != reconciled={reconciled}"

    print("\n[+] SUCCESS: Stage 15 accounting strictly balanced with zero loss!")
    print("==================================================================")


if __name__ == "__main__":
    main()
