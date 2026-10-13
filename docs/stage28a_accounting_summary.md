# Stage 28A Zero-Loss Accounting Summary

Every logical evaluation item resolves into **exactly one mutually exclusive category**:
$$\text{Expected} = \text{NativeUnmodified} + \text{NativeRepaired} + \text{SafetyFallback} + \text{ProviderFallback} + \text{Failed} + \text{NotAttempted} + \text{Unaccounted}$$
$$\text{Duplicates} = 0, \quad \text{MissingItems} = 0, \quad \text{Unaccounted} = 0$$

---

## 1. Accounting Breakdown: Clean Locked Subset (Expected = 39 Items)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Unaccounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B1** | Lexical Substitution Baseline | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B2** | Sentence Splitting Baseline | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B3** | Syntactic Rules Baseline | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B4** | Combined Deterministic Baseline | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B5** | Offline Deterministic Fallback | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **C1** | Stage 25 Controlled Engine | 39 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **G1** | Gemini Native Simplification | 29 | 0 | 0 | 10 | 0 | 0 | 0 | **CONSERVED** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 28 | 0 | 1 | 10 | 0 | 0 | 0 | **CONSERVED** |
| **T1** | mT5 Native Simplification | 0 | 0 | 0 | 0 | 0 | 39 | 0 | **CONSERVED** |
| **T2** | mBART Native Simplification | 0 | 0 | 0 | 0 | 0 | 39 | 0 | **CONSERVED** |

---

## 2. Accounting Breakdown: External ASSET Benchmark (Expected = 359 Items)

| System ID | System Name | Native Unmod. | Native Repaired | Safety Fallback | Provider Fallback | Failed | Not Attempted | Unaccounted | Conservation Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **B0** | Identity Baseline | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B1** | Lexical Substitution Baseline | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B2** | Sentence Splitting Baseline | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B3** | Syntactic Rules Baseline | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B4** | Combined Deterministic Baseline | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **B5** | Offline Deterministic Fallback | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **C1** | Stage 25 Controlled Engine | 359 | 0 | 0 | 0 | 0 | 0 | 0 | **CONSERVED** |
| **G1** | Gemini Native Simplification | 0 | 0 | 0 | 359 | 0 | 0 | 0 | **CONSERVED** |
| **H1** | Stage 26 Governed Hybrid Pipeline | 0 | 0 | 0 | 359 | 0 | 0 | 0 | **CONSERVED** |
| **T1** | mT5 Native Simplification | 0 | 0 | 0 | 0 | 0 | 359 | 0 | **CONSERVED** |
| **T2** | mBART Native Simplification | 0 | 0 | 0 | 0 | 0 | 359 | 0 | **CONSERVED** |
