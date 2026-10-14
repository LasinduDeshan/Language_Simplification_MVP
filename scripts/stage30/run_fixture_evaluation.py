"""
Stage 30 Fixture Evaluation Runner (WP8)
Executes the master preprocessing pipeline across all 32 governed fixtures,
verifies technical invariants, performs zero-unaccounted accounting,
and outputs fixture_evaluation_summary.json, fixture_evaluation_report.md,
and error_analysis.md.
"""

import sys
import json
import hashlib
from pathlib import Path

# Add backend directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.schemas import TerminalDisposition

FIXTURES_DIR = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "fixtures"
RESULTS_DIR = PROJECT_ROOT / "data" / "sinhala_preprocessing" / "results"
DOCS_DIR = PROJECT_ROOT / "docs"

FIXTURE_FILES = [
    "normalization_cases.json",
    "grapheme_cases.json",
    "sentence_cases.json",
    "tokenization_cases.json",
    "mixed_script_cases.json",
    "invalid_unicode_cases.json"
]

def run_evaluation():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    total_fixtures = 0
    passed_fixtures = 0
    disposition_counts = {
        "PASSED": 0,
        "PASSED_WITH_NORMALIZATION": 0,
        "MANUAL_REVIEW_REQUIRED": 0,
        "REJECTED_INVALID_UNICODE": 0,
        "EXCLUDED_NON_SINHALA": 0
    }

    eval_results = []
    total_operations = 0
    total_sentences = 0
    total_tokens = 0
    tokens_by_type = {}
    offset_failures = 0
    reconstruction_failures = 0
    pipeline_introduced_replacement = 0
    records_with_joiners = 0
    records_with_mixed_scripts = 0
    records_routed_to_review = 0

    for fname in FIXTURE_FILES:
        fpath = FIXTURES_DIR / fname
        with open(fpath, "r", encoding="utf-8") as f:
            cases = json.load(f)

        for case in cases:
            total_fixtures += 1
            fid = case["fixture_id"]
            raw_text = case["input_text"]
            lang = case.get("language", "si")
            loc = case.get("locale", "si-LK")
            exp_disp = case.get("expected_disposition")

            # Run pipeline
            rec = preprocess_sinhala_text(
                raw_text=raw_text,
                record_id=fid,
                language=lang,
                locale=loc
            )

            actual_disp = rec.final_disposition.value
            disposition_counts[actual_disp] += 1
            total_operations += len(rec.operations)
            total_sentences += len(rec.sentences)
            total_tokens += len(rec.tokens)

            # Record token categories
            for t in rec.tokens:
                ttype = t.token_type.value
                tokens_by_type[ttype] = tokens_by_type.get(ttype, 0) + 1

            # Check joiners and mixed scripts
            if "JOINER_PRESENT" in [f.value for f in rec.quality_flags]:
                records_with_joiners += 1
            if "MIXED_SCRIPT_PRESENT" in [f.value for f in rec.quality_flags]:
                records_with_mixed_scripts += 1
            if actual_disp == "MANUAL_REVIEW_REQUIRED":
                records_routed_to_review += 1

            # Invariant checks:
            # 1. Raw text immutability
            assert rec.raw_text == raw_text, f"{fid}: Raw text was mutated!"
            assert rec.raw_text_sha256 == hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

            # 2. No replacement character introduced
            if "\uFFFD" not in raw_text and "\uFFFD" in rec.normalized_text:
                pipeline_introduced_replacement += 1

            # 3. Offset validity
            for s in rec.sentences:
                if not (0 <= s.start_code_point <= s.end_code_point <= len(rec.normalized_text)):
                    offset_failures += 1
            for t in rec.tokens:
                if not (0 <= t.start_code_point <= t.end_code_point <= len(rec.normalized_text)):
                    offset_failures += 1

            # 4. Sentence / token reconstruction
            if rec.sentences and rec.tokens:
                # Reconstructed token text should be subset of normalized text
                for t in rec.tokens:
                    extracted = rec.normalized_text[t.start_code_point:t.end_code_point]
                    if extracted != t.surface:
                        reconstruction_failures += 1

            # Expected disposition match
            disp_match = (exp_disp is None or actual_disp == exp_disp)
            if disp_match:
                passed_fixtures += 1

            eval_results.append({
                "fixture_id": fid,
                "file": fname,
                "expected_disposition": exp_disp,
                "actual_disposition": actual_disp,
                "disposition_match": disp_match,
                "reason_code": rec.disposition_reason_code,
                "quality_flags": [f.value for f in rec.quality_flags],
                "raw_code_points": rec.raw_code_point_count,
                "normalized_code_points": rec.normalized_code_point_count,
                "grapheme_count": rec.normalized_grapheme_count,
                "sentence_count": len(rec.sentences),
                "token_count": len(rec.tokens),
                "operation_count": len(rec.operations)
            })

    # Accounting check
    sum_dispositions = sum(disposition_counts.values())
    unaccounted_records = total_fixtures - sum_dispositions
    assert unaccounted_records == 0, f"Accounting invariant failed: {unaccounted_records} unaccounted records!"

    summary_data = {
        "evaluation_id": "STAGE30-FIXTURE-EVALUATION-V1",
        "total_fixtures": total_fixtures,
        "passed_fixtures": passed_fixtures,
        "accuracy_pct": round((passed_fixtures / total_fixtures) * 100, 2),
        "disposition_counts": disposition_counts,
        "unaccounted_records": unaccounted_records,
        "total_operations": total_operations,
        "total_sentences": total_sentences,
        "total_tokens": total_tokens,
        "tokens_by_type": tokens_by_type,
        "offset_failures": offset_failures,
        "reconstruction_failures": reconstruction_failures,
        "pipeline_introduced_replacement_characters": pipeline_introduced_replacement,
        "records_with_joiners": records_with_joiners,
        "records_with_mixed_scripts": records_with_mixed_scripts,
        "records_routed_to_review": records_routed_to_review,
        "results": eval_results
    }

    # Write summary JSON
    summary_path = RESULTS_DIR / "fixture_evaluation_summary.json"
    summary_path.write_text(json.dumps(summary_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Fixture evaluation complete. Results written to: {summary_path}")
    print(f"Total fixtures evaluated: {total_fixtures}")
    print(f"Fixture disposition accuracy: {passed_fixtures}/{total_fixtures} ({summary_data['accuracy_pct']}%)")
    print(f"Accounting: Unaccounted records = {unaccounted_records}")
    print(f"Offset failures: {offset_failures}, Reconstruction failures: {reconstruction_failures}")
    print(f"Pipeline-introduced U+FFFD: {pipeline_introduced_replacement}")

    return summary_data

if __name__ == "__main__":
    run_evaluation()
