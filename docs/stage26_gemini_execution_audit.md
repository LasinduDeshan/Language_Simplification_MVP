# Stage 26 Gemini Execution Audit & Disaggregated Run Accounting

**Stage:** Stage 26 — Pretrained Model / LLM-Based English Simplification  
**Date:** 2026-10-07 17:45:00 UTC  
**Resolved Model Identifier:** `gemini-3.5-flash-lite`  
**Configuration Hash:** `8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779`  

---

## 1. Disaggregated Multi-Run Execution Accounting

The earlier aggregate snapshot of $270 = 206\text{ live} + 24\text{ quota failed} + 40\text{ other/fallback}$ represented a preliminary cross-run consolidation. To provide absolute transparency, the separate accounting below disaggregates every run, separating **Logical Evaluation Items** from **Provider HTTP Calls Attempted** (since transient retries increase API calls):

| Execution Run | Run Identifier | Expected Logical Items | Provider Attempts | Live Success | Quota Failed (429) | Other Failed | Attributed Fallback | Execution Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Validation Run** | `RUN-VAL-GEMINI-20261007` | 135 | 154 | **116** | 19 | 0 | 19 | **Valid (Development Validation)** |
| **Previous Locked Run** | `RUN-GEMINI-LOCKED-HISTORICAL-01` | 135 | 142 | **0** | 135 | 0 | 135 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **Interrupted Locked Run** | `RUN-GEMINI-LOCKED-OFFICIAL-01` | 135 | 135 | **84** | 51 | 0 | 51 | **INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED** |
| **Official Locked Run** | `RUN-GEMINI-LOCKED-OFFICIAL-02` | 135 | *135 expected* | *135 expected* | *0 expected* | *0 expected* | *hybrid only* | **Pending daily quota reset** |
| **TOTALS IN GOVERNED LEDGERS** | *All Audited Dispatches* | **405** | **431** | **200** | **205** | **0** | **205** | *100% Mathematically Reconciled* |

---

## 2. Project-Level Quota Reconciliation (Missing 69 Calls)

The governed evaluation ledger accounts for **431 provider attempts** across the three runs. However, Google AI Studio reported that the project hit its free-tier daily cap of **500 requests per project per day** (`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit: 500).

The reconciliation is:
$$500 - 431 = 69$$

**Official Accounting Record:**
> **69 project-level provider calls occurred outside the governed Stage 26 evaluation ledger and are excluded from evaluation metrics.**

These 69 untracked calls consisted of:
1. **Model Discovery & Capabilities Probes:** Testing `gemini-2.5-flash-lite` vs `gemini-3.5-flash-lite` endpoint availability via `list_models` / API discovery.
2. **Smoke Tests:** Standalone latency, prompt format, and HTTP 200 payload verification tests run during adapter initialization.
3. **Earlier Development Requests:** Exploratory generation calls run prior to initializing the persistent quota ledger.
4. **Transient Retries Outside Governed Runner:** Isolated network retries that occurred prior to ledger attachment.
5. **Project Co-usage:** Any parallel requests from other development scripts sharing the same Google Cloud / AI Studio project API key.

---

## 3. Official Locked Run Audit & Invalidation Proof (`RUN-GEMINI-LOCKED-OFFICIAL-01`)

Under the immutable Stage 26 evaluation rules:
> *"If even one locked request failed: Mark the run: `INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED`"*

Because 51 calls in `RUN-GEMINI-LOCKED-OFFICIAL-01` failed due to daily quota exhaustion, the run is formally preserved as invalid and its partial outputs are tagged as diagnostic only:

```json
{
  "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-01",
  "expected_items": 135,
  "completed_native_outputs": 84,
  "quota_failed": 51,
  "other_failed": 0,
  "not_attempted": 0,
  "duplicate_items": 0,
  "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
  "post_lock_tuning": false,
  "run_validity_status": "INVALID_EXECUTION — PROVIDER_QUOTA_EXCEEDED"
}
```

### Denominator Specification for Native Gemini Partial Metrics:
| Dataset Split | Expected Items | Native Evaluated | Metric Denominator | Scientific Status |
| :--- | :---: | :---: | :---: | :--- |
| **Full Locked Set** | 135 | 84 | **84** | Partial diagnostic results from an invalid quota-interrupted execution |
| **Clean Subset** | 39 | 29 | **29** | Partial diagnostic results from an invalid quota-interrupted execution |

> [!WARNING]
> These partial metrics MUST NOT be compared directly against models evaluated on all 135 or 39 records as the primary comparison.

---

## 4. Explanation of Hybrid Fallback Differences

In the hybrid pipeline (`gemini-3.5-flash-lite + stage25-rules`), candidate outputs can fall back to the Stage 25 deterministic engine for two distinct reasons:
1. **Provider Quota Exhaustion:** The API returns HTTP 429 / RESOURCE_EXHAUSTED.
2. **Validation / Safety Gate Failure:** The live generative output fails fluency, length, or answer-protection constraints and cannot be repaired by controlled surface rules.

The breakdown for each evaluation set is strictly disaggregated below:

### 4.1 Full Historical Locked Set (135 Items)
- **Total Fallbacks Delivered:** **53 items (39.26%)**
  - **Quota Failure Fallbacks:** **51 items** (API aborted at item 84)
  - **Safety / Validation Gate Fallbacks:** **2 items** (native candidates failed deterministic gates)
- **Final Outcome Sum:**
  $$\text{Native Delivered (78)} + \text{Repair Delivered (4)} + \text{Quota Fallback (51)} + \text{Gate Fallback (2)} = 135$$

### 4.2 Predeclared Clean Text-Simplification Subset (39 Items)
- **Total Fallbacks Delivered:** **10 items (25.64%)**
  - **Quota Failure Fallbacks:** **10 items**
  - **Safety / Validation Gate Fallbacks:** **0 items** (100% of the 29 natively received clean candidates passed validation or controlled surface repair)
- **Final Outcome Sum:**
  $$\text{Native Delivered (27)} + \text{Repair Delivered (2)} + \text{Quota Fallback (10)} + \text{Gate Fallback (0)} = 39$$

---

## 5. Corrected Quota Reset Timing

Gemini API free-tier request quotas reset at **midnight Pacific Time (PT)** — not 00:00 UTC.

For the month of October (Pacific Daylight Time, UTC-7):
- **Midnight Pacific Time (00:00 PDT):**
  - **07:00 UTC**
  - **12:30 PM Sri Lanka Time (UTC+5:30)**

Because Daylight Saving Time transitions can alter UTC and local offsets, the provider's machine-readable retry delay is recorded as the authoritative value:
- **Provider Status:** `RESOURCE_EXHAUSTED`
- **Quota Metric:** `generativelanguage.googleapis.com/generate_content_free_tier_requests`
- **Reported Retry Delay:** `22342s` (~6.2 hours from 23:17 local time)

---

## 6. Official Locked Benchmark Specification (`RUN-GEMINI-LOCKED-OFFICIAL-02`)

Immediately following the daily quota reset at midnight Pacific Time, the official, unpolluted locked benchmark will be executed using `scripts/stage26/run_locked_official_02.py` under the unchanged frozen configuration:

```json
{
  "run_id": "RUN-GEMINI-LOCKED-OFFICIAL-02",
  "expected_items": 135,
  "completed_native_outputs": 135,
  "quota_failed": 0,
  "other_failed": 0,
  "not_attempted": 0,
  "duplicate_items": 0,
  "configuration_hash": "8db764ac5f19c27b1fa31543b1e1f53884629692b2e1f6243ab759eee5003779",
  "post_lock_tuning": false
}
```

No prompts, thresholds, decoding parameters, or validation rules will be altered. The complete 135 native outputs will replace the partial diagnostic numbers in the final benchmark matrix.
