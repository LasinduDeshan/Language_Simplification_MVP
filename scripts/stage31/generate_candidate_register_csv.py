"""
Generate docs/stage31_candidate_source_register.csv from data/sinhala_external/registry/candidate_sources.json.
"""

import csv
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "registry" / "candidate_sources.json"
CSV_PATH = PROJECT_ROOT / "docs" / "stage31_candidate_source_register.csv"

def generate_csv():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    sources = data.get("sources", [])

    fieldnames = [
        "source_id",
        "source_name",
        "publisher",
        "source_class",
        "language_claim",
        "primary_decision",
        "licence_name",
        "licence_version",
        "access_method",
        "robots_txt_status",
        "canonical_url_sanitized",
        "notes"
    ]

    with open(CSV_PATH, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in sources:
            writer.writerow({
                "source_id": s["source_id"],
                "source_name": s["source_name"],
                "publisher": s["publisher"],
                "source_class": s["source_class"],
                "language_claim": s["language_claim"],
                "primary_decision": s["primary_decision"],
                "licence_name": s.get("licence_name") or "None",
                "licence_version": s.get("licence_version") or "None",
                "access_method": s["acquisition_policy"]["access_method"],
                "robots_txt_status": s["acquisition_policy"]["robots_txt_status"],
                "canonical_url_sanitized": s["canonical_url_sanitized"],
                "notes": s.get("notes", "")
            })

    print(f"Generated {CSV_PATH} with {len(sources)} candidate sources.")

if __name__ == "__main__":
    generate_csv()
