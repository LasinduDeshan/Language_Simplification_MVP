"""
Stage 30 Determinism Verifier.
Runs repeated passes across all governed fixtures to verify 100% determinism.
"""

import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.serialization import record_to_dict

FIXTURES_DIR = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "fixtures"

def verify_determinism():
    total_checked = 0
    for fixture_file in FIXTURES_DIR.glob("*.json"):
        with open(fixture_file, "r", encoding="utf-8") as f:
            cases = json.load(f)
        for c in cases:
            text = c["input_text"]
            fid = c["fixture_id"]
            lang = c.get("language", "si")
            loc = c.get("locale", "si-LK")

            r1 = preprocess_sinhala_text(text, record_id=fid, language=lang, locale=loc)
            r2 = preprocess_sinhala_text(text, record_id=fid, language=lang, locale=loc)

            d1 = record_to_dict(r1)
            d2 = record_to_dict(r2)

            assert d1 == d2, f"Determinism failure on fixture {fid}"
            total_checked += 1

    print(f"Determinism verified across {total_checked} fixture passes. Result: PASSED")

if __name__ == "__main__":
    verify_determinism()
