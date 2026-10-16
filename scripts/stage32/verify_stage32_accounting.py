"""
Comprehensive Accounting and Invariant Verifier for Stage 32 (WP9).
Reconciles all 5 levels of accounting:
1. Corpus input accounting (150 canonical records, 180 provenance records).
2. Token occurrence accounting (4072 total, 0 unaccounted).
3. Candidate entry accounting (1010 total, 0 unaccounted).
4. Provisional band accounting (sum of bands = 1010).
5. Duplicate weight reconciliation (sum of weights = 150.0).
"""

import collections
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CANONICAL_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "canonical_analytical_corpus.jsonl"
PROVENANCE_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "corpus" / "pilot_corpus.jsonl"
OCCURRENCE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "token_occurrence_ledger.jsonl"
CANDIDATE_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "candidate_entry_ledger.jsonl"
WEIGHT_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "provenance_weight_ledger.jsonl"
DRAFT_LEXICON_PATH = PROJECT_ROOT / "data" / "sinhala_lexicon" / "lexicon" / "draft_lexicon.jsonl"
MAPPING_LEDGER = PROJECT_ROOT / "data" / "sinhala_lexicon" / "ledgers" / "surface_form_mapping.jsonl"

def verify_all_accounting():
    print("=== Stage 32 Comprehensive Accounting Verification ===")

    # Level 1: Corpus Input Accounting
    with open(CANONICAL_PATH, "r", encoding="utf-8") as f:
        canonical_count = sum(1 for line in f if line.strip())
    with open(PROVENANCE_PATH, "r", encoding="utf-8") as f:
        provenance_count = sum(1 for line in f if line.strip())

    print(f"Level 1 (Corpus): Canonical = {canonical_count} (Expected: 150) | Provenance = {provenance_count} (Expected: 180)")
    assert canonical_count == 150
    assert provenance_count == 180

    # Level 2: Token Occurrence Accounting
    occ_counts = collections.Counter()
    total_tokens = 0
    with open(OCCURRENCE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                total_tokens += 1
                occ_counts[rec["occurrence_disposition"]] += 1

    included_tokens = occ_counts["INCLUDED_CANDIDATE_OCCURRENCE"]
    excluded_tokens = occ_counts["EXCLUDED_TOKEN_CLASS"]
    review_tokens = occ_counts["MANUAL_REVIEW_OCCURRENCE"]
    rejected_tokens = occ_counts["REJECTED_PRIVACY_OR_SECURITY"] + occ_counts["REJECTED_INVALID_SOURCE_EVIDENCE"]
    unaccounted_tokens = total_tokens - (included_tokens + excluded_tokens + review_tokens + rejected_tokens)

    print(f"Level 2 (Occurrences): Total = {total_tokens} | Included = {included_tokens} | Excluded = {excluded_tokens} | Review = {review_tokens} | Unaccounted = {unaccounted_tokens}")
    assert unaccounted_tokens == 0
    assert total_tokens == 4072
    assert included_tokens == 3668

    # Level 3: Candidate Entry Accounting
    entry_counts = collections.Counter()
    total_entries = 0
    with open(CANDIDATE_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                total_entries += 1
                entry_counts[rec["terminal_entry_disposition"]] += 1

    accepted_entries = entry_counts["ACCEPTED_DRAFT_LEXICON_ENTRY"]
    review_entries = entry_counts["MANUAL_REVIEW_REQUIRED"]
    excluded_entries = entry_counts["EXCLUDED_NON_LEXICAL"] + entry_counts["EXCLUDED_NON_SINHALA"]
    rejected_entries = entry_counts["REJECTED_PRIVACY_OR_SECURITY"] + entry_counts["REJECTED_INVALID_SOURCE_EVIDENCE"]
    unaccounted_entries = total_entries - (accepted_entries + review_entries + excluded_entries + rejected_entries)

    print(f"Level 3 (Candidate Entries): Total = {total_entries} | Accepted = {accepted_entries} | Review = {review_entries} | Excluded = {excluded_entries} | Unaccounted = {unaccounted_entries}")
    assert unaccounted_entries == 0
    assert total_entries == 1010
    assert accepted_entries == 1001
    assert review_entries == 9

    # Level 4: Provisional Band Accounting
    band_counts = collections.Counter()
    total_draft = 0
    with open(DRAFT_LEXICON_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                total_draft += 1
                band_counts[rec["provisional_band"]] += 1

    print(f"Level 4 (Provisional Bands): Total = {total_draft} | Breakdown = {dict(band_counts)}")
    assert total_draft == 1010
    assert sum(band_counts.values()) == 1010

    # Level 5: Duplicate Weight Reconciliation (Stage 32 Derived Rational Weight Ledger)
    from fractions import Fraction
    rational_weights = []
    float_weights = []
    weight_records_count = 0
    with open(WEIGHT_LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                weight_records_count += 1
                num = rec.get("duplicate_weight_numerator", 1)
                den = rec.get("duplicate_weight_denominator", 1)
                rational_weights.append(Fraction(num, den))
                float_weights.append(float(rec.get("duplicate_weight_float", 1.0)))
                assert rec.get("authoritative_weight_representation") == "rational", "Representation must be rational"

    assert weight_records_count == 180, f"Expected 180 weight records, got {weight_records_count}"
    sum_rational = sum(rational_weights)
    sum_float = sum(float_weights)
    float_delta = abs(sum_float - 150.0)
    print(f"Level 5 (Duplicate Weights): Exact Rational Total = {sum_rational} (Expected: 150) | Float Sum = {sum_float:.14f} | Float Diagnostic Delta = {float_delta:.16e}")
    assert sum_rational == 150, f"Exact rational weight total must be 150, got {sum_rational}"
    assert float_delta <= 1e-12, f"Float diagnostic delta {float_delta} exceeds 1e-12 tolerance!"
    print("  [OK] Exact rational weight total: 150 | Float diagnostic delta <= 1e-12 | Accounting status: PASSED")

    # Level 6: Entry-Source Membership and Rights Profile Accounting
    APPROVED_SOURCES_PATH = PROJECT_ROOT / "data" / "sinhala_external" / "registry" / "approved_sources.json"
    with open(APPROVED_SOURCES_PATH, "r", encoding="utf-8") as f:
        src_reg = json.load(f)
    approved_map = {
        s["source_id"]: (s["rights_profile_id"], s["rights_profile_version"])
        for s in src_reg.get("sources", [])
    }

    total_memberships = 0
    single_source_count = 0
    multi_source_count = 0
    source_counts = collections.Counter()
    missing_rights = 0
    unregistered_sources = 0

    with open(DRAFT_LEXICON_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                refs = rec.get("rights_profile_refs", [])
                if not refs:
                    missing_rights += 1
                n_src = len(refs)
                total_memberships += n_src
                if n_src == 1:
                    single_source_count += 1
                elif n_src > 1:
                    multi_source_count += 1

                for ref in refs:
                    sid = ref["source_id"]
                    source_counts[sid] += 1
                    if sid not in approved_map:
                        unregistered_sources += 1
                    else:
                        exp_rpid, exp_ver = approved_map[sid]
                        assert ref["rights_profile_id"] == exp_rpid
                        assert ref["rights_profile_version"] == exp_ver

    print(f"Level 6 (Memberships): Distinct Entries = {total_draft} | Memberships = {total_memberships} | Multi-Source = {multi_source_count} | Single-Source = {single_source_count}")
    print(f"  Source Breakdown: {dict(source_counts)}")
    print(f"  Missing Rights Refs: {missing_rights} | Unregistered Sources: {unregistered_sources}")

    assert total_draft == 1010
    assert total_memberships == 1194
    assert single_source_count == 872
    assert multi_source_count == 138
    assert single_source_count + multi_source_count == 1010
    assert missing_rights == 0
    assert unregistered_sources == 0
    assert source_counts["SRC-SI-001"] == 448
    assert source_counts["SRC-SI-002"] == 207
    assert source_counts["SRC-SI-003"] == 179
    assert source_counts["SRC-SI-004"] == 215
    assert source_counts["SRC-SI-008"] == 145
    assert sum(source_counts.values()) == 1194

    print("=== All 6 Accounting Levels PASSED with ZERO Unaccounted Units & Invariant Verified ===")
    return True

if __name__ == "__main__":
    verify_all_accounting()

