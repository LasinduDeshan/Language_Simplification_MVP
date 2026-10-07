# Stage 14 Dataset Schemas, Versions & Metadata Conversion Report

**Generated:** 2026-09-23T17:02:52.743847Z  
**Branch:** `feature/dataset-scoring`  

## 1. Executive Summary

Stage 14 formalized machine-readable V1 dataset schemas (version `1.0.0`) and published initial content release `0.1.0`.
- **Adaptation Test Set**: 40 activities converted to V1 with child-safe answer boundaries.
- **Simplification Corpus**: 210 draft pairs converted to V1 (retaining `validation_status='draft'`, `research_eligible=false`, `approved_for_child_delivery=false`).
- **Lexicon Repository**: 18 tiered vocabulary entries converted to V1.
- **Schema Registry & JSON Schemas**: Generated 7 JSON Schemas and published schema registry.

## 2. Published Release Artifacts & Checksums

| File Path | Size (Bytes) | SHA-256 Hash |
|---|---|---|
| `data/adaptation_test_set/releases/0.1.0/adaptation_test_set.json` | 89541 | `ec18dcfd50daa55e5f214b0f7194b1f8bc8e8436bddba859416e4c5321efe0b4` |
| `data/simplification_corpus/releases/0.1.0/simplification_corpus.json` | 393078 | `45df6c344d3724b2f646fcdef2de770ead78af459c5f6940001ba9a024a52ade` |
| `data/lexicons/en/releases/0.1.0/lexicon_repository.json` | 24351 | `5d4ee20464c5a48ec277fd24ae04ab016837d5e4efbe48a182d972e5ea11cb49` |
| `data/schemas/1.0.0/common_metadata.schema.json` | 6088 | `a8ffff578ef8a7e80af76ac057d09c63cb5d08392b42374a020917573acea3a4` |
| `data/schemas/1.0.0/adaptation_record.schema.json` | 12556 | `b0723a86a208ab950842bb53e2ca898300fdd688da25da6cd9b9972bb77e10cd` |
| `data/schemas/1.0.0/simplification_pair.schema.json` | 13303 | `756c550e4ae5eac18122caa52ced7fa8e3823839e79c8c1558f36a89f358a37f` |
| `data/schemas/1.0.0/interaction_record.schema.json` | 9048 | `288d2ac2660949c2bc9f4675583cef53ca8a6943f325b4e5c68668a8e44dcff2` |
| `data/schemas/1.0.0/interaction_export.schema.json` | 3707 | `73b79c6169fa88b993eac5f4eee11bac3b17ea2a22a6e0c28472b50769d8ce9e` |
| `data/schemas/1.0.0/lexicon_entry.schema.json` | 9256 | `90d423c8d7849ac673af044f88dbf8922470718d232cbe4ce3038aa5bd687c8f` |
| `data/schemas/1.0.0/release_manifest.schema.json` | 4768 | `483cdc214b7010bbf4110cf27c2cd8ac511ca1aa4bcdb4580117896ed04e8a51` |
| `data/schemas/registry.json` | 1086 | `4213284f7ef1ed5bcea498c05302c15d94cb7d669cb4f2f0f36c64fa8423e004` |
| `docs/stage14_field_dictionary.csv` | 15738 | `4f60965a88c98b0cb661759356e85b105f9390935659650036ee8ee5e64d662f` |
| `docs/dataset_versioning_policy.md` | 2454 | `2490dba1c26f8c38dfd5bf6df542c4720466eb15d53aca0381d724806b5a26a7` |
| `docs/dataset_rights_and_permissions.md` | 2737 | `6be160f2e75083fa97a290837dc6c1ded375513957ecca06633589b4da8261f0` |

## 3. Governance Invariants Confirmed

- All Stage 13 unique identifiers preserved.
- Rights metadata enforces default-restrictive settings.
- Screening risk indicator remains owned by Component 1 and read-only.
- External benchmark datasets (ASSET/TurkCorpus/WikiLarge) deferred to Stage 20.
- Multilingual schema readiness established; zero Sinhala records added.
