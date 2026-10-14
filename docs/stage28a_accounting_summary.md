# Stage 28A Zero-Loss Accounting Summary

Every logical evaluation item resolves into **exactly one mutually exclusive category**:
$$\text{Expected} = \text{NativeUnmodified} + \text{NativeRepaired} + \text{SafetyFallback} + \text{ProviderFallback} + \text{Failed} + \text{NotAttempted} + \text{Unaccounted}$$
$$\text{Duplicates} = 0, \quad \text{MissingItems} = 0, \quad \text{Unaccounted} = 0$$

### Dispatch Population Accounting
- Unique locked inputs: 135
- Clean-subset membership: 39
- Total locked provider dispatch population: 135
- Duplicate dispatches: 0
- Executed 135 unique locked items once. The predeclared 39-item clean subset was derived from those same outputs without additional model calls.

---

## 1. Accounting Breakdown: Clean Locked Subset (N=39)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Total Accounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **B1** | Lexical Substitution Baseline | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **B2** | Sentence Splitting Baseline | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **B3** | Syntactic Rules Baseline | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **B4** | Combined Deterministic Baseline | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **B5** | Offline Deterministic Fallback | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **C1** | Stage 25 Controlled Engine | 39 | 0 | 0 | 0 | 0 | 0 | **39/39** | **CONSERVED** |
| **G1** | Gemini Native Simplification | 29 | 0 | 0 | 10 | 0 | 0 | **39/39** | **CONSERVED** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 28 | 0 | 1 | 10 | 0 | 0 | **39/39** | **CONSERVED** |
| **T1** | mT5 Native Simplification | 0 | 0 | 0 | 0 | 0 | 39 | **39/39** | **CONSERVED** |
| **T2** | mBART Native Simplification | 0 | 0 | 0 | 0 | 0 | 39 | **39/39** | **CONSERVED** |

---

## 2. Disaggregated Provider Outcome Accounting (Gemini G1 Dispatches)

| Provider Outcome Category | Clean Subset Count ($N=39$) | Clean Subset Rate (%) | Full Benchmark Count ($N=135$) | Full Benchmark Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Native Success (HTTP 200)** | 29 | 74.4% | 84 | 62.2% |
| **Daily-quota exhaustion (`DAILY_QUOTA_FAILED`, HTTP 429)** | 6 | 15.4% | 39 | 28.9% |
| **Transient rate limit after retries (`RATE_LIMIT_FAILED`, HTTP 429)** | 4 | 10.3% | 12 | 8.9% |
| **HTTP 503 after retries** | 0 | 0.0% | 0 | 0.0% |
| **Timeout / network exhaustion** | 0 | 0.0% | 0 | 0.0% |
| **Other provider failure** | 0 | 0.0% | 0 | 0.0% |
| **Total Provider Fallbacks Delivered** | **10** | **25.6%** | **51** | **37.8%** |

### HTTP Attempt Population Accounting
- **Clean Subset ($N=39$):** 29 single-attempt successes + 6 single-attempt daily quota stops + 16 retry attempts (4 rate-limit items $\times$ 4 jittered retries) = **51 HTTP calls** across 39 logical requests (average 1.31 calls/request).
- **Full Benchmark ($N=135$):** 84 single-attempt successes + 39 single-attempt daily quota stops + 48 retry attempts (12 rate-limit items $\times$ 4 retries) = **171 HTTP calls** across 135 logical requests (average 1.27 calls/request).

---

## 3. Accounting Breakdown: External ASSET Benchmark (N=359, Fixed Generic Mode)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Total Accounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **B1** | Lexical Substitution Baseline | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **B2** | Sentence Splitting Baseline | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **B3** | Syntactic Rules Baseline | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **B4** | Combined Deterministic Baseline | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **B5** | Offline Deterministic Fallback | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **C1** | Stage 25 Controlled Engine | 359 | 0 | 0 | 0 | 0 | 0 | **359/359** | **CONSERVED** |
| **G1** | Gemini Native Simplification | 0 | 0 | 0 | 359 | 0 | 0 | **359/359** | **CONSERVED** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 0 | 0 | 0 | 359 | 0 | 0 | **359/359** | **CONSERVED** |
| **T1** | mT5 Native Simplification | 0 | 0 | 0 | 0 | 0 | 359 | **359/359** | **CONSERVED** |
| **T2** | mBART Native Simplification | 0 | 0 | 0 | 0 | 0 | 359 | **359/359** | **CONSERVED** |
