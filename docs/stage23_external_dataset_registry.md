# Stage 23 External Dataset Registry & Rights Verification Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** External English Datasets  
**Governance Standard:** Stage 23 Legal Rights and Content Licensing Policy  
**Status:** FORMALLY EVALUATED & SEALED  

---

## 1. Registry Decisions Summary

| Dataset ID | Dataset Name | Rights Status | Content Licence | Local Processing | Benchmark Use | Training Use | Redistribution |
|---|---|---|---|:---:|:---:|:---:|:---:|
| `EXTDATA-ASSET` | ASSET | `approved_local_research` | CC-BY-NC 4.0 | Yes | Yes | No | No |
| `EXTDATA-TURKCORPUS` | TurkCorpus | `approved_local_research` | CC-BY-SA 4.0 / Academic | Yes | Yes | No | No |
| `EXTDATA-OASISSIMP-EN` | OasisSimp-English | `approved_local_research` | CC-BY 4.0 | Yes | Yes | No | No |
| `EXTDATA-WIKILARGE-PILOT` | WikiLarge Pilot | `approved_local_research` | CC-BY-SA 3.0 (Wikipedia) | Yes | No | Yes (Pilot) | No |
| `EXTDATA-NEWSELA` | Newsela | `excluded_rights` | Proprietary Copyright | No | No | No | No |

---

## 2. Granular Evaluation Records

### 2.1 ASSET (`EXTDATA-ASSET`)
- **Official Source:** [facebookresearch/asset](https://github.com/facebookresearch/asset)
- **Publication:** Alva-Manchego et al. (ACL 2020)
- **Licence:** Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)
- **Role:** Primary Multi-Reference Evaluation Benchmark (2,359 source groups, 23,590 references).
- **Restrictions:** Non-commercial research use only; raw corpus redistribution prohibited; benchmark isolation enforced.

### 2.2 TurkCorpus (`EXTDATA-TURKCORPUS`)
- **Official Source:** [cocoxu/simplification](https://github.com/cocoxu/simplification)
- **Publication:** Xu et al. (TACL 2016)
- **Licence:** CC-BY-SA 4.0 / Academic Open Access
- **Role:** Standard SARI-Compatible Multi-Reference Benchmark (2,359 source groups, 18,872 references).
- **Restrictions:** Shares source sentences with ASSET; benchmark isolation enforced.

### 2.3 OasisSimp-English (`EXTDATA-OASISSIMP-EN`)
- **Official Source:** [OasisSimpDataset.github.io](https://OasisSimpDataset.github.io/)
- **Publication:** De Silva et al. (2024)
- **Licence:** Creative Commons Attribution 4.0 International (CC-BY 4.0)
- **Role:** Cross-domain and future English–Sinhala bridge benchmark.
- **Restrictions:** Locked to `benchmark_only` for Release 0.1.0.

### 2.4 WikiLarge Pilot (`EXTDATA-WIKILARGE-PILOT`)
- **Official Source:** [XingxingZhang/dress](https://github.com/XingxingZhang/dress)
- **Publication:** Zhang & Lapata (EMNLP 2017)
- **Licence:** CC-BY-SA 3.0 (Wikipedia Lineage)
- **Role:** Optional Filtered Large-Scale Pilot Training Reference.
- **Status:** Isolated non-blocking pilot.

### 2.5 Newsela (`EXTDATA-NEWSELA`)
- **Official Source:** [newsela.com/data](https://newsela.com/data/)
- **Publication:** Xu et al. (TACL 2015)
- **Licence:** Proprietary Commercial / Restricted Institutional Agreement
- **Disposition:** `excluded_rights` (Excluded from automated acquisition and processing).
