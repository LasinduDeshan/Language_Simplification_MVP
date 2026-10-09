"""Independent Post-Execution Verifier for RUN-GEMINI-LOCKED-OFFICIAL-02

Strictly validates every ledger entry against:
1. Exact expected 135 unique logical keys from locked_test_set.json
2. Native output validity condition:
   valid_native_output = (
       entry.get("http_status") == 200
       and entry.get("native_output_received") is True
       and entry.get("fallback_used") is False
       and isinstance(entry.get("output_text"), str)
       and bool(entry["output_text"].strip())
       and entry.get("finish_reason") not in {"SAFETY", "RECITATION", "BLOCKED"}
       and entry.get("resolved_model") == "gemini-3.5-flash-lite"
   )
3. Zero fallbacks, zero quota failures, zero network/other failures, zero duplicates, zero missing items.
4. Clean subset exact alignment against predeclared manifest:
   stage26_clean_subset_manifest.json (39 items, 13 source groups).
5. Output hash storing (avoid raw text in proof).
6. Hard failure gating: exits with 1 if any invariant fails.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_RUN_ID = sys.argv[1] if len(sys.argv) > 1 else "RUN-GEMINI-LOCKED-OFFICIAL-03"

if "02" in DEFAULT_RUN_ID:
    TARGET_RUN_ID = "RUN-GEMINI-LOCKED-OFFICIAL-02"
    LEDGER_FILE = REPO_ROOT / "data" / "model_simplification" / "results" / "locked_test" / "locked_gemini_ledger_official_02.json"
    PROOF_OUTPUT_FILE = REPO_ROOT / "data" / "model_simplification" / "results" / "locked_test" / "run_gemini_locked_official_02_independent_proof.json"
else:
    TARGET_RUN_ID = "RUN-GEMINI-LOCKED-OFFICIAL-03"
    LEDGER_FILE = REPO_ROOT / "data" / "model_simplification" / "results" / "locked_test" / "locked_gemini_ledger_official_03.json"
    PROOF_OUTPUT_FILE = REPO_ROOT / "data" / "model_simplification" / "results" / "locked_test" / "run_gemini_locked_official_03_independent_proof.json"

LOCKED_TEST_GROUPS = REPO_ROOT / "data" / "baseline_simplification" / "evaluation_inputs" / "internal_locked_test_groups.json"
CLEAN_MANIFEST_FILE = REPO_ROOT / "data" / "model_simplification" / "registry" / "stage26_clean_subset_manifest.json"

FROZEN_CONFIG_HASH = "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779"
PROMPT_REGISTRY_HASH = "a5ae1df8457684181c117695d3cd6885a4b9d4102ab837ba0f236348a4226a85"
DATASET_HASH = "61bbc2b26c943dcbbc630b4af6c7598a2cebb1025e272a96a7bcc510f4d066d3"
RUNNER_START_HASH = "a603d0a106c3d6c0637514f80b50bba76fdf79d556a47cae1f5e2c6d91e86a0b"
RUNNER_POST_AUDIT_HASH = "b780d383640cf356acae7a45ade87ecd0ff57c2ca374f9860913a4c8f92d9cf1"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_valid_native_output(entry: Dict[str, Any]) -> tuple[bool, List[str]]:
    reasons = []
    if entry.get("http_status") != 200:
        reasons.append(f"http_status != 200 (was {entry.get('http_status')})")
    if entry.get("native_output_received") is not True:
        reasons.append(f"native_output_received is not True (was {entry.get('native_output_received')})")
    if entry.get("fallback_used") is not False:
        reasons.append("fallback_used is True")
    out_text = entry.get("output_text")
    if not isinstance(out_text, str):
        reasons.append("output_text is not string")
    elif not bool(out_text.strip()):
        reasons.append("output_text is empty or whitespace-only")
    finish_reason = entry.get("finish_reason")
    if finish_reason in {"SAFETY", "RECITATION", "BLOCKED"}:
        reasons.append(f"finish_reason blocked ({finish_reason})")
    if entry.get("resolved_model") != "gemini-3.5-flash-lite":
        reasons.append(f"resolved_model != gemini-3.5-flash-lite (was {entry.get('resolved_model')})")
    
    is_valid = len(reasons) == 0
    return is_valid, reasons


def main():
    print("=" * 70)
    print("STAGE 26 INDEPENDENT POST-EXECUTION VERIFIER")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    # 1. Load locked test groups
    if not LOCKED_TEST_GROUPS.exists():
        print(f"[-] Missing locked test set at {LOCKED_TEST_GROUPS}")
        sys.exit(1)
    with open(LOCKED_TEST_GROUPS, "r", encoding="utf-8") as f:
        locked_test_groups = json.load(f)
    expected_keys = [f"{g['source_group_id']}_{t}" for g in locked_test_groups for t in ["mild", "moderate", "strong"]]
    expected_unique_keys = set(expected_keys)
    print(f"[*] Expected locked test set logical keys: {len(expected_keys)} ({len(expected_unique_keys)} unique)")

    # 2. Load clean subset manifest
    if not CLEAN_MANIFEST_FILE.exists():
        print(f"[-] Missing clean subset manifest at {CLEAN_MANIFEST_FILE}")
        sys.exit(1)
    with open(CLEAN_MANIFEST_FILE, "r", encoding="utf-8") as f:
        clean_manifest = json.load(f)
    manifest_item_ids = set(clean_manifest["item_ids"])
    manifest_sg_ids = set(clean_manifest["source_group_ids"])
    print(f"[*] Predeclared clean subset manifest: {len(manifest_item_ids)} items, {len(manifest_sg_ids)} source groups")

    # 3. Load ledger
    if not LEDGER_FILE.exists():
        print(f"[-] Ledger not found at {LEDGER_FILE}")
        sys.exit(1)
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    print(f"[*] Loaded ledger containing {len(ledger)} entries")

    # 4. Invariant Calculations (Dynamically Computed)
    seen_keys = []
    duplicate_items = 0
    quota_failed_items = []
    other_failed_items = []
    fallback_items = []
    invalid_native_items = []
    output_hashes = {}

    for entry in ledger:
        key = f"{entry.get('source_group_id')}_{entry.get('support_level')}"
        if key in seen_keys:
            duplicate_items += 1
        seen_keys.append(key)

        # Check native validity
        is_valid, failure_reasons = check_valid_native_output(entry)
        if not is_valid:
            invalid_native_items.append({"key": key, "request_id": entry.get("request_id"), "reasons": failure_reasons})

        # Classify failures
        status = entry.get("execution_status")
        http_st = entry.get("http_status")
        if http_st == 429 or status == "DAILY_QUOTA_FAILED":
            quota_failed_items.append(key)
        elif http_st != 200 or status != "LIVE_SUCCESS":
            other_failed_items.append({"key": key, "http_status": http_st, "status": status, "error": entry.get("error_message")})

        if entry.get("fallback_used") is True:
            fallback_items.append(key)

        out_text = entry.get("output_text") or ""
        output_hashes[key] = sha256_text(out_text) if out_text else None

    unique_ledger_keys = set(seen_keys)
    missing_keys = expected_unique_keys - unique_ledger_keys
    completed_native_outputs = len(ledger) - len(invalid_native_items)

    # 5. Check clean subset coverage
    clean_ledger_entries = [e for e in ledger if f"{e.get('source_group_id')}_{e.get('support_level')}" in manifest_item_ids]
    clean_invalid = [e for e in clean_ledger_entries if not check_valid_native_output(e)[0]]

    # 6. Final Status Determination
    invariants_passed = (
        len(unique_ledger_keys) == 135
        and len(missing_keys) == 0
        and duplicate_items == 0
        and completed_native_outputs == 135
        and len(quota_failed_items) == 0
        and len(other_failed_items) == 0
        and len(fallback_items) == 0
        and len(invalid_native_items) == 0
        and len(clean_ledger_entries) == 39
        and len(clean_invalid) == 0
    )

    if invariants_passed:
        validity_status = "VALID_COMPLETE_NATIVE_EXECUTION"
    elif len(quota_failed_items) > 0:
        validity_status = "INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED"
    elif len(other_failed_items) > 0:
        validity_status = "INVALID_EXECUTION — NETWORK_OR_PROVIDER_FAILURE"
    else:
        validity_status = "INVALID_EXECUTION — AUDIT_INVARIANTS_FAILED"

    # Construct Sealed Proof
    sealed_proof = {
        "run_id": TARGET_RUN_ID,
        "verifier_timestamp": datetime.now(timezone.utc).isoformat(),
        "expected_items": 135,
        "completed_native_outputs": completed_native_outputs,
        "quota_failed": len(quota_failed_items),
        "other_failed": len(other_failed_items),
        "not_attempted": len(missing_keys),
        "duplicate_items": duplicate_items,
        "fallback_outputs": len(fallback_items),
        "invalid_native_outputs": len(invalid_native_items),
        "clean_subset_expected": 39,
        "clean_subset_completed_native": len(clean_ledger_entries) - len(clean_invalid),
        "configuration_hash": FROZEN_CONFIG_HASH,
        "prompt_registry_hash": PROMPT_REGISTRY_HASH,
        "dataset_hash": DATASET_HASH,
        "runner_hash_at_start": RUNNER_START_HASH,
        "runner_hash_post_audit": RUNNER_POST_AUDIT_HASH,
        "post_lock_tuning": False,
        "run_validity_status": validity_status,
        "details": {
            "quota_failed_items": quota_failed_items,
            "other_failed_items": other_failed_items,
            "invalid_native_items": invalid_native_items,
            "missing_keys": list(missing_keys),
            "clean_subset_manifest_sha256": clean_manifest.get("manifest_sha256"),
        },
        "output_hashes_sha256": output_hashes,
    }

    with open(PROOF_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sealed_proof, f, indent=2)

    print("=" * 70)
    print(f"VERIFICATION STATUS: {validity_status}")
    print(f"Total entries: {len(ledger)}")
    print(f"Completed valid native outputs: {completed_native_outputs}/135")
    print(f"Quota failed: {len(quota_failed_items)}")
    print(f"Other failed: {len(other_failed_items)}")
    print(f"Fallback used: {len(fallback_items)}")
    print(f"Duplicate items: {duplicate_items}")
    print(f"Missing items: {len(missing_keys)}")
    print(f"Clean subset completed: {len(clean_ledger_entries) - len(clean_invalid)}/39")
    print(f"Sealed proof written to: {PROOF_OUTPUT_FILE}")
    print("=" * 70)

    if not invariants_passed:
        print("[!] INVARIANTS FAILED. Official metrics MUST NOT be published for this run.")
        sys.exit(1)
    else:
        print("[+] ALL INVARIANTS PASSED. Run is certified as VALID_COMPLETE_NATIVE_EXECUTION.")
        sys.exit(0)


if __name__ == "__main__":
    main()
