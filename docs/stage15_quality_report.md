# Stage 15 — Automated Dataset Quality Validation Report

**Run ID:** `VAL-20260924-f880b408`  
**Generated Date:** 2026-09-26 13:35:00 UTC  
**Target Scope:** English MVP, Children Aged 4–8  
**Quality Rule-Set Version:** `1.0.0`  
**Dataset Schema Version:** `1.0.0`  

---

## 1. Executive Summary & Disposition Breakdown

| Dataset Layer | Evaluated Records | Passed | Failed | Manual Review | Quarantined |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Adaptation Test Set** | 40 | 40 | 0 | 0 | 0 |
| **Simplification Corpus** | 210 | 160 | 19 | 31 | 0 |
| **Lexicon Repository** | 18 | 18 | 0 | 0 | 0 |
| **Interaction Export Fixtures** | *472 (Test fixtures)* | *472* | *0* | *0* | *0* |
| **TOTAL GOVERNED RECORDS** | **268** | **218** | **19** | **31** | **0** |

$$\text{Total Governed Records (268)} = \text{Passed (218)} + \text{Failed (19)} + \text{Review Required (31)} + \text{Quarantined (0)}$$
$$\text{Unaccounted Records} = 0$$

> **Note on Interaction Exports**: No production interaction export was available. Privacy validation was verified using controlled valid and intentionally leaking test fixtures. These fixtures are excluded from the governed dataset record total.

---

## 2. Breakdown of the 50 Non-Passing Records

All 50 non-passing records have been preserved and routed to the Stage 16 manual review queue:

| Main Issue | Rule ID | Severity | Failed Records | Review Records | Quarantined | Description |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Quantity / Number Divergence** | `SIMP-NUM-003` | Error | 15 | 0 | 0 | Numerical or count entity altered during draft simplification |
| **Negation Polarity Inconsistency** | `SIMP-NEG-002` | Error | 6 | 0 | 0 | Polarity inversion or dropped negation in draft simplified pair |
| **Compression / Length Divergence** | `SIMP-COMP-007` | Warning | 0 | 15 | 0 | Length expansion ($>1.20\times$) or compression ($<0.30\times$) |
| **Lexicon Example Sentence Missing** | `LEX-EXSENT-006` | Warning | 0 | 18 | 0 | Draft lexicon entry missing child example usage sentence |
| **Lexicon Complexity Proxy** | `LEX-COMP-007` | Warning | 0 | 1 | 0 | Synonym replacement exceeds headword character length |
| **TOTAL UNIQUE RECORDS** | — | — | **19** | **31** | **0** | **50 total non-passing records queued for Stage 16 review** |

---

## 3. Governance Invariants & Draft Status Lock

Explicit verification of draft governance across all 210 Simplification Corpus pairs:
- **210 / 210** `validation_status = "draft"`
- **210 / 210** `research_eligible = false`
- **210 / 210** `approved_for_child_delivery = false`
- **210 / 210** `requires_expert_review = true`

> The 160 automatically passed records are **not** expert-approved records. Automatic validation is advisory and cannot grant child delivery or research eligibility.

---

## 4. Safety-Test Evidence (Intentional Leak Fixtures)

Controlled test fixtures with intentional defects verified the safety boundary:
- **Protected-answer leak fixture**: `PASSED` — Detected as `CRITICAL` (`SAFE-LEAK-001`), record quarantined.
- **PII leak fixture (Email/Phone)**: `PASSED` — Detected as `CRITICAL` (`PRIV-PII-002`), record quarantined.
- **Unsafe export field fixture**: `PASSED` — Detected as `CRITICAL` (`PRIV-ALLOW-001`), record quarantined.
- **Validation run blocked on critical failure**: `PASSED` — Prevents release of compromised datasets.

---

## 5. Database & Migration Verification

- **Alembic Migration Script**: `backend/alembic/versions/a15b8c9d0e1f_stage15_quality_validation_tables.py`
- **Revision ID**: `a15b8c9d0e1f` (down_revision: `91ee0a12abcd`)
- **`alembic current`**: `a15b8c9d0e1f (head)`
- **`alembic heads`**: `a15b8c9d0e1f (head)`
- **Lifecycle Test**: Verified `upgrade` $\rightarrow$ `downgrade` $\rightarrow$ `re-upgrade` on database copy preserving all existing application tables (`learner_profiles`, `tasks`, `activity_sessions`).
