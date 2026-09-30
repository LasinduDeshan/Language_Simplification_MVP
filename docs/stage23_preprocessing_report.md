# Stage 23 External Dataset Preprocessing Report

**Dataset:** ASSET (Alva-Manchego et al., ACL 2020)  
**Execution Timestamp:** 2026-09-30 07:06:53 UTC  
**Pipeline Version:** 1.0.0 (Stage 21 Preprocessing & Normalization Engine)  
**Status:** COMPLETED & BITWISE VERIFIED  

---

## 1. Accounting Summary

| Split | Source Groups | References per Source | Total Reference Instances | Missing References | Unaccounted Sources |
|---|:---:|:---:|:---:|:---:|:---:|
| Validation | 2,000 | 10 | 20,000 | 0 | 0 |
| Test | 359 | 10 | 3,590 | 0 | 0 |
| **Total** | **2,359** | **10** | **23,590** | **0** | **0** |

---

## 2. Normalization Operations Applied

- **Unicode Canonical Normalization:** NFC representation applied to all source strings and 10 reference strings.
- **Whitespace Harmonization:** Redundant whitespace and linebreaks condensed to single spaces; leading/trailing whitespace stripped.
- **Dual Representation Guarantee:** Raw downloaded strings are preserved byte-for-byte in `raw_source_text` and `raw_references`. Evaluation views are derived deterministically.
- **Non-Mutation Rule:** Official benchmark sentences were not altered or shortened during preprocessing.
