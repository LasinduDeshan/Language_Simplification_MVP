# Stage 33 — Accounting Reconciliation Summary

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Mutually exclusive conservation equations across inputs, attempts, candidates, operations, and export boundaries  
**Evaluation View:** Canonical Analytical Corpus View (`canonical_analytical_150`)  
**Status:** Reconciled with Zero Unaccounted Units  

---

## 1. Accounting Framework Overview

Stage 33 implements exact conservation accounting across 6 levels using mutually exclusive terminal statuses.

---

## 2. Level 1: Input Disposition Accounting

$$\text{SubmittedInputs} = \text{DraftRewriteSelected} + \text{UnchangedNoApplicableRule} + \text{UnchangedAllBlocked} + \text{ManualReviewRequired} + \text{RejectedSourceIneligible} + \text{RejectedInvalidState} + \text{FailedInternal} + \text{Unaccounted}$$

| Partition | Submitted | Draft Selected | Unchanged No Rule | Unchanged Blocked | Manual Review | Failed Internal | Unaccounted |
|---|---|---|---|---|---|---|---|
| **Train Split** | 124 | 54 | 70 | 0 | 0 | 0 | **0** |
| **Validation Split** | 13 | 8 | 5 | 0 | 0 | 0 | **0** |
| **Locked-Test Split** | 13 | 9 | 4 | 0 | 0 | 0 | **0** |
| **Total Canonical View** | **150** | **71** | **79** | **0** | **0** | **0** | **0** |

---

## 3. Level 2: Rule Attempt Accounting

$$\text{RuleAttempts} = \text{CANDIDATE\_GENERATED} + \text{NOT\_APPLICABLE} + \text{BLOCKED\_PROTECTED\_SPAN} + \text{BLOCKED\_MEANING\_GUARD} + \text{DEFERRED\_MANUAL\_REVIEW} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

| Partition | Total Attempts | Candidate Generated | Not Applicable | Blocked Guard | Blocked Span | Review Deferred | Unaccounted |
|---|---|---|---|---|---|---|---|
| **Train Split** | 1,001 | 74 | 922 | 5 | 0 | 0 | **0** |
| **Validation Split** | 105 | 13 | 90 | 2 | 0 | 0 | **0** |
| **Locked-Test Split** | 104 | 12 | 92 | 0 | 0 | 0 | **0** |
| **Total Canonical View** | **1,210** | **99** | **1,104** | **7** | **0** | **0** | **0** |

---

## 4. Level 3: Candidate Accounting

$$\text{GeneratedCandidates} = \text{SELECTED} + \text{NOT\_SELECTED\_LOWER\_RANK} + \text{BLOCKED\_PROTECTED\_SPAN} + \text{BLOCKED\_MEANING\_GUARD} + \text{DEFERRED\_MANUAL\_REVIEW} + \text{FAILED\_INTERNAL} + \text{Unaccounted}$$

| Partition | Total Candidates | Selected | Lower Rank | Blocked Guard | Blocked Span | Review Deferred | Unaccounted |
|---|---|---|---|---|---|---|---|
| **Train Split** | 74 | 54 | 20 | 0 | 0 | 0 | **0** |
| **Validation Split** | 13 | 8 | 5 | 0 | 0 | 0 | **0** |
| **Locked-Test Split** | 12 | 9 | 3 | 0 | 0 | 0 | **0** |
| **Total Canonical View** | **99** | **71** | **28** | **0** | **0** | **0** | **0** |

---

## 5. Level 4: Transformation Operation Accounting

$$\text{RecordedOperations} = \text{Replacements} + \text{Splits} + \text{Deletions} + \text{Insertions} + \text{Reorders} + \text{Unaccounted}$$

- **Replacements (`REPLACE`):** 36
- **Splits (`SPLIT`):** 36
- **Deletions (`DELETE`):** 2
- **Total Operations:** 74
- **Unaccounted Operations:** **0**

---

## 6. Level 5 & 6: Rights and Export Accounting

- **Evaluated Export Fields:** 100% compliant with public metadata contracts.
- **Literal restricted text leaked into public ledgers:** **0**
- **Unaccounted export fields:** **0**
