# Stage 35 Dataset Partition and Disclosure Report

**Stage:** Stage 35 — Comparative Evaluation of Gemini, mT5, and mBART for Sinhala Simplification  
**Denominator Specification Reference:** `data/model_comparison/stage35/registry/stage35_locked_test_denominators.json`  

---

## 1. Locked-Test Input Denominators

The Stage 35 locked test set comprises exactly $N = 13$ source items drawn from the sealed Stage 31/33 corpus, partitioned according to privacy and disclosure permissions:

| Partition Tier | Count ($N$) | Source IDs | Rights & Transmission Policy | Eligible Conditions |
|---|---|---|---|---|
| **Primary Common Denominator** | $N_{\text{common}} = 8$ | `SRC-SI-001`, `SRC-SI-003` | Public/permissive; cloud API disclosure permitted | C0, C1, C2, C3 |
| **Local-Only Supplementary Denominator** | $N_{\text{local}} = 5$ | `SRC-SI-002`, `SRC-SI-004` | Confidential/restricted; on-premise execution only; external API transmission strictly PROHIBITED | C0, C2, C3 (C1 BLOCKED) |
| **Total Test Inputs** | $N = 13$ | All 13 items | Complete sealed evaluation set | C0 (13), C1 (8), C2 (13), C3 (13) |

---

## 2. Level 2 Potential Pairs and Disclosure Reconciliation

With 13 test inputs and 4 registered conditions, there are 52 potential condition-input pairs:
$$13 \times 4 = 52 \text{ potential pairs}$$

Under the frozen data-governance and privacy policy, Condition C1 (`C1_GEMINI_ZERO_SHOT`) is strictly prohibited from transmitting the 5 local-only items to external Google cloud endpoints. Consequently, 5 pairs are blocked at the disclosure gate before execution scheduling.

The exact, non-contradictory Level 2 reconciliation is:
$$52 \text{ potential pairs} = 47 \text{ eligible executions} + 5 \text{ disclosure-blocked pairs}$$
$$47 \text{ eligible executions} = 47 \text{ started} + 0 \text{ not started}$$

### Condition-Level Execution Breakdown

| Condition | Common Inputs ($N=8$) | Local-Only Inputs ($N=5$) | Disclosure-Blocked Pairs | Eligible Executions | Executions Started | Executions Not Started |
|---|---|---|---|---|---|---|
| `C0_RULE_BASELINE` | 8 | 5 | 0 | 13 | 13 | 0 |
| `C1_GEMINI_ZERO_SHOT` | 8 | 0 | 5 | 8 | 8 | 0 |
| `C2_MT5_ZERO_SHOT` | 8 | 5 | 0 | 13 | 13 | 0 |
| `C3_MBART_ZERO_SHOT` | 8 | 5 | 0 | 13 | 13 | 0 |
| **Total** | **32** | **15** | **5** | **47** | **47** | **0** |

Zero-loss accounting: $\text{Unaccounted} = 0$.
