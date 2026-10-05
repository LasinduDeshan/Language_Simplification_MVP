# Stage 26 — Corpus Accounting & Precedence Summary

**Document Version:** 1.1.0  
**Date:** 2026-10-05  
**Authoritative Prerequisite Tag:** `stage-25-complete-v2` (`6b785502b860d4e93d2d31b86bd653c33a210ac9`)  

---

## 1. Reconciled 4-Class Mutually Exclusive Pair Accounting ($N=900$ Pairs)

To prevent contamination of model training pools, source group contamination propagates to all pairs within that source group:

| Disposition Class | Train Split | Val Split | Test Split | Total Pairs | Direct Pair Defect | Group Eligibility | Internal Training Decision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `task_reformulation_excluded` | 225 | 49 | 52 | **326** | `True` | `False` | `excluded_from_training` |
| `source_group_reformulation_excluded` | 195 | 0 | 0 | **195** | `False` | `False` | `excluded_from_training` |
| `non_development_split_excluded` | 0 | 86 | 83 | **169** | `False` | `False` / `True` | `excluded_from_training` |
| `eligible_for_internal_model_development` | 210 | 0 | 0 | **210** | `False` | `True` | `approved_for_pilot_fine_tuning` |
| **Total** | **630** | **135** | **135** | **900** | — | — | **100.0% Mutually Exclusive** |

$$\text{Accounting Balance: } 326 + 195 + 169 + 210 = 900$$

---

## 2. Reconciled Source-Group Hierarchy Accounting ($N=300$ Groups)

| Precedence Rank | Group Classification Class | Train Groups | Val Groups | Test Groups | Total Groups | Pairs Impacted |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `task_reformulation_group_excluded` | 140 | 32 | 31 | **203** | $140 \times 3 = 420$ Train pairs (225 direct + 195 contaminated) |
| 2 | `non_development_group_excluded` | 0 | 13 | 14 | **27** | 81 pairs (39 Val, 42 Test) |
| 7 | `eligible_internal_training_group` | 70 | 0 | 0 | **70** | $70 \times 3 = 210$ clean training pairs |
| **Total** | | **210** | **45** | **45** | **300** | **900 Pairs** |

$$\text{Group Balance: } 203 + 27 + 70 = 300$$
