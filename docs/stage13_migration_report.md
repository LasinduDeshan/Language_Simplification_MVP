# Stage 13 Dataset Separation & Governance Migration Report

**Generated:** 2026-09-23T14:25:24.796896Z  
**Branch:** `feature/dataset-scoring`  

## 1. Executive Summary

Stage 13 separated the English MVP data into three governed layers:
1. **Adaptation Test Set** (`data/adaptation_test_set/`): Local simulated activities.
2. **Simplification Corpus** (`data/simplification_corpus/`): Original-simplified sentence pairs.
3. **Interaction Dataset** (`data/interaction_dataset/`): Private runtime interaction evidence.

## 2. Published Files and Integrity Checksums

| File Path | Size (Bytes) | SHA-256 Hash |
|---|---|---|
| `data/adaptation_test_set/en/component3_local_samples/c3_local_tasks.json` | 65508 | `8effeb41bd08b7ab...` |
| `data/adaptation_test_set/id_mappings/task_id_mappings.json` | 19282 | `48206fdddea64d18...` |
| `data/simplification_corpus/en/draft/draft_pairs.json` | 137479 | `e6645cfb06722b78...` |
| `data/simplification_corpus/annotations/grammar_error_annotations.json` | 2961 | `d1e6022ba3c7603f...` |
| `data/simplification_corpus/id_mappings/corpus_id_mappings.json` | 78111 | `b4723ed860bd354d...` |
| `data/lexicons/en/tiered_vocabulary_lexicon.json` | 4479 | `5d134e33c1432e67...` |
| `docs/stage13_dataset_inventory.csv` | 6174 | `934f39591cf332fc...` |
| `docs/stage13_classification_rules.md` | 3874 | `c9e7156e85bf0c8e...` |
| `docs/stage13_master_id_mappings.csv` | 67286 | `efe884daf2c79eac...` |

## 3. Governance Boundaries Confirmed

- **Component 1**: Retains ownership of DLD risk screening indicator and screening activities.
- **Component 2**: Retains ownership of AR 3D assets and action sequencing.
- **Component 3**: Owns language simplification test set and corpus; does not own production Activity Bank.
- **Component 4**: Owns official longitudinal trends; receives exported evidence with `local_preliminary_trend`.
