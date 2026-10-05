# Stage 26 — Corpus Accounting & Precedence Summary

**Document Version:** 1.0.0  
**Date:** 2026-10-05  
**Authoritative Prerequisite:** `stage-25-complete-v2`  

---

## 1. 7-Class Precedence Hierarchy Accounting ($N=900$ Pairs)

| Precedence Rank | Eligibility Class | Pair Count | Train | Val | Test | Action / Impact |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `task_reformulation_excluded` | 326 | 225 | 49 | 52 | Excluded from training/fine-tuning |
| 2 | `non_development_split_excluded` | 169 | 0 | 86 | 83 | Evaluation splits preserved clean |
| 3 | `incomplete_source_group_excluded` | 0 | 0 | 0 | 0 | All source groups complete |
| 4 | `rights_or_governance_excluded` | 0 | 0 | 0 | 0 | Internal developmental rights clear |
| 5 | `quality_failed` | 0 | 0 | 0 | 0 | Stage 25 quality verified |
| 6 | `manual_review_unresolved` | 0 | 0 | 0 | 0 | Reviews tracked |
| 7 | `eligible_for_internal_model_development` | 405 | 405 | 0 | 0 | Eligible internal training pairs |
| **Total** | | **900** | **630** | **135** | **135** | **100% Accounted** |

---

## 2. Source-Group Hierarchy Accounting ($N=300$ Groups)

| Precedence Rank | Group Class | Group Count | Split Distribution | Impact |
| :---: | :--- | :---: | :--- | :--- |
| 1 | `task_reformulation_group_excluded` | 203 | 140 Train, 32 Val, 31 Test | Task reformulations isolated |
| 2 | `non_development_group_excluded` | 27 | 13 Val, 14 Test | Clean evaluation groups |
| 7 | `eligible_internal_training_group` | 70 | 70 Train ($70 \times 3 = 210$ pairs) | Clean complete 3-tier training groups |
| **Total** | | **300** | **210 Train, 45 Val, 45 Test** | **100% Accounted** |
