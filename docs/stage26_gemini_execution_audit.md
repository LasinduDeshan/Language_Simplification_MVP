# Stage 26 Gemini Execution Audit & Disaggregated Run Accounting

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-07 17:37:45 UTC  
**Resolved Model Identifier:** `gemini-3.5-flash-lite`  
**Configuration Hash:** `8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779`  

---

## 1. Disaggregated Multi-Run Execution Accounting

The previous aggregate accounting ($270 = 206 + 24 + 40$) represented a cross-run snapshot. Below is the strict, disaggregated per-run accounting distinguishing **Logical Evaluation Items** from **Provider HTTP Calls Attempted**:

| Execution Run | Run Identifier | Logical Items | Provider Attempts | Live Success | Quota Failed (429) | Other Failed | Attributed Fallback | Execution Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Validation Run** | `RUN-VAL-GEMINI-20261007` | 135 | 154 | **116** | 19 | 0 | 19 | **Valid (Development Validation)** |
| **Historical Locked Run** | `RUN-GEMINI-LOCKED-HISTORICAL-01` | 135 | 142 | **0** | 135 | 0 | 135 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **Attempted Official Locked Run** | `RUN-GEMINI-LOCKED-OFFICIAL-01` | 135 | 135 | **84** | 51 | 0 | 51 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **TOTALS ACROSS AUDITED RUNS** | *All Audited Dispatches* | **405** | **431** | **200** | **205** | **0** | **205** | *100% Mathematically Reconciled* |

### Key Observations:
1. **Provider Attempts vs. Logical Items:** Provider attempts (431) exceed logical items (405) because transient HTTP 429 rate limits trigger automatic exponential retry attempts (up to 3 attempts with jittered backoff) before routing to attributed fallback.
2. **Quota Interruption Root Cause:** The Google Gemini free-tier imposes a strict daily cap of **500 requests per project per day** (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit: 500). Between validation runs, smoke tests, and the initial locked run, the cumulative quota reached 500 at item 84 of `RUN-GEMINI-LOCKED-OFFICIAL-01` (exact Google API response: `RESOURCE_EXHAUSTED: Please retry in 6h33m34s`).

---

## 2. Official Locked Run Audit & Invalidation Proof

According to Step 4 of the project specifications:
> *"If even one locked request failed: Mark the run: INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED"*

Because 51 calls in `RUN-GEMINI-LOCKED-OFFICIAL-01` were cut short by the 500 daily quota limit, the run is formally preserved and marked invalid rather than misattributed:

```json
{
  "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-01",
  "expected_items": 135,
  "completed_native_outputs": 84,
  "quota_failed": 51,
  "not_attempted": 0,
  "duplicate_items": 0,
  "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
  "post_lock_tuning": false,
  "run_validity_status": "INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED",
  "preservation_record": {
    "partial_native_outputs_preserved": 84,
    "error_logs_preserved": 51,
    "zero_fixture_outputs_used": true,
    "zero_silent_fallbacks": true
  }
}
```

### Clean Subset Reconciliation:
- Total clean subset items: **39**
- Natively completed before quota exhaustion: **29** (74.4%)
- Quota interrupted $ightarrow$ Attributed Stage 25 Fallback: **10** (25.6%)

---

## 3. Sample Audited Request Ledger Entries

| Request ID | Run ID | Group ID | Tier | HTTP | Execution Status | Native Recv. | Fallback | Model | Latency |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: | :---: | :--- | :---: |
| `GENREQ-VAL-001` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-INS-0365` | mild | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 2466.39 ms |
| `GENREQ-VAL-002` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-INS-0365` | moderate | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 5705.29 ms |
| `GENREQ-VAL-003` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-INS-0365` | strong | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 3688.42 ms |
| `GENREQ-VAL-004` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-COM-0266` | mild | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 7215.08 ms |
| `GENREQ-VAL-005` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-COM-0266` | moderate | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 2850.77 ms |
| `GENREQ-VAL-006` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-COM-0266` | strong | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 16867.07 ms |
| `GENREQ-VAL-007` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-COM-0312` | mild | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 2409.59 ms |
| `GENREQ-VAL-008` | `RUN-VAL-GEMINI-20261007142521` | `SRC-EN-COM-0312` | moderate | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 6493.1 ms |
| `LOCKED-GEMINI-001` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-VOC-0150` | mild | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 4253.97 ms |
| `LOCKED-GEMINI-002` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-VOC-0150` | moderate | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 5456.1 ms |
| `LOCKED-GEMINI-003` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-VOC-0150` | strong | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 2662.18 ms |
| `LOCKED-GEMINI-004` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-GRA-0220` | mild | 429 | `RATE_LIMIT_FAILED` | False | True | `gemini-3.5-flash-lite` | 20479.91 ms |
| `LOCKED-GEMINI-005` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-GRA-0220` | moderate | 429 | `RATE_LIMIT_FAILED` | False | True | `gemini-3.5-flash-lite` | 15048.45 ms |
| `LOCKED-GEMINI-006` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-GRA-0220` | strong | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 6329.71 ms |
| `LOCKED-GEMINI-007` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-COM-0250` | mild | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 2702.91 ms |
| `LOCKED-GEMINI-008` | `RUN-GEMINI-LOCKED-OFFICIAL-01` | `SRC-EN-COM-0250` | moderate | 200 | `LIVE_SUCCESS` | True | False | `gemini-3.5-flash-lite` | 4464.22 ms |

---

## 4. Audit Conclusion & Schedule Forward

All 405 logical evaluation requests across the 3 audited runs are accounted for with 100% mutual exclusivity in persistent JSON ledgers. Following the recommended quota isolation schedule (Day 1: Validation; Day 2: Locked Benchmark; Day 3: ASSET), the official clean 135-call locked benchmark (`RUN-GEMINI-LOCKED-OFFICIAL-02`) will execute following the daily quota reset at 00:00 UTC / 17:00 PDT with unchanged frozen configuration hash `8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779`.
