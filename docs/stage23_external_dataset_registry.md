# Stage 23 External Dataset Registry & Rights Verification Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** External English Datasets  
**Governance Standard:** Stage 23 Legal Rights and Content Licensing Policy  
**Status:** FORMALLY EVALUATED (COMMIT-PINNED PRIMARY EVIDENCE VERIFIED)  

---

## 1. Registry Decisions Summary

| Dataset ID | Dataset Name | Rights Status | Content Licence | Local Processing | Benchmark Use | Training Use | Primary Evidence Status |
|---|---|---|---|:---:|:---:|:---:|---|
| `EXTDATA-ASSET` | ASSET | `approved_local_research` | CC-BY-NC 4.0 | **Yes** | **Yes** | **No** | Verified via commit-pinned LICENSE file at `9d659040d0d8942dbc4cd65cf357563b43fd9ab4` (`50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447`) |
| `EXTDATA-TURKCORPUS` | TurkCorpus | `pending_content_rights_verification` | *Pending* | **No** | **No** | **No** | Pending content license verification (GPL-3.0 is code license only) |
| `EXTDATA-OASISSIMP-EN` | OasisSimp-English | `pending_content_rights_verification` | *Pending* | **No** | **No** | **No** | Pending explicit archive license verification |
| `EXTDATA-WIKILARGE-PILOT` | WikiLarge Pilot | `pending_lineage_and_rights_verification` | *Pending* | **No** | **No** | **No** | Pending Wikipedia alignment lineage and training rights verification |
| `EXTDATA-NEWSELA` | Newsela | `excluded_rights` | Proprietary Copyright | **No** | **No** | **No** | Formally excluded without written permission |

---

## 2. Granular Evaluation Records

### 2.1 ASSET (`EXTDATA-ASSET`) — Approved for Local Research
- **Official Source:** [facebookresearch/asset](https://github.com/facebookresearch/asset)
- **Publication:** Alva-Manchego et al. (ACL 2020)
- **Primary Evidence Type:** `dataset_license_file`
- **Commit SHA:** `9d659040d0d8942dbc4cd65cf357563b43fd9ab4`
- **Commit-Pinned Evidence URL:** `https://raw.githubusercontent.com/facebookresearch/asset/9d659040d0d8942dbc4cd65cf357563b43fd9ab4/LICENSE`
- **Local Snapshot:** `data/external_english/asset/manifests/LICENSE`
- **Primary Evidence SHA-256:** `50f03face87211373b7a447607f9ca26ad95ad339e8293ac2807958bad7b5447`
- **Evidence Scope:** `dataset_content`
- **Verified Licence:** Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC 4.0)
- **Intended Use Context:** `noncommercial_academic_research`
- **Role:** Primary Multi-Reference Evaluation Benchmark (2,359 source groups, 23,590 references).
- **Permissions:** `local_processing_allowed: true`, `benchmark_use_allowed: true`, `training_use_allowed: false`, `redistribution_allowed: false`, `derived_feature_release_allowed: true`.
- **Redistribution Policy:** Raw and normalized ASSET text are Git-ignored and kept in local cache only. Release artifacts contain only non-reconstructable feature summaries, indices, and evaluation metrics.

### 2.2 TurkCorpus (`EXTDATA-TURKCORPUS`) — Pending Content Rights
- **Official Source:** [cocoxu/simplification](https://github.com/cocoxu/simplification)
- **Publication:** Xu et al. (TACL 2016)
- **Primary Evidence Scope:** `repository_software` (Repository is GPL-3.0).
- **Status:** `pending_content_rights_verification` until exact licensing for Wikipedia sentences and crowdsourced MTurk references is verified.

### 2.3 OasisSimp-English (`EXTDATA-OASISSIMP-EN`) — Pending Content Rights
- **Official Source:** [OasisSimpDataset.github.io](https://OasisSimpDataset.github.io/)
- **Publication:** De Silva et al. (2024)
- **Status:** `pending_content_rights_verification` until official dataset archive license file is verified.

### 2.4 WikiLarge Pilot (`EXTDATA-WIKILARGE-PILOT`) — Pending Lineage
- **Official Source:** [XingxingZhang/dress](https://github.com/XingxingZhang/dress)
- **Publication:** Zhang & Lapata (EMNLP 2017)
- **Status:** `pending_lineage_and_rights_verification` (MIT code license in DRESS does not prove Wikipedia alignment dataset license).

### 2.5 Newsela (`EXTDATA-NEWSELA`) — Excluded
- **Official Source:** [newsela.com/data](https://newsela.com/data/)
- **Publication:** Xu et al. (TACL 2015)
- **Status:** `excluded_rights` (Proprietary commercial news dataset requiring individual institutional data use agreements).
