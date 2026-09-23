# Dataset Versioning & Schema Evolution Policy

**Component:** Component 3 — AI/NLP-Based Personalized Language Simplification  
**Scope:** Adaptation Test Set, Simplification Corpus, Interaction Dataset, Lexicon Repository  
**Initial Schema Version:** `1.0.0`  
**Initial Dataset Content Version:** `0.1.0`

---

## 1. Dual Versioning Framework

To prevent confusion between structural data models and linguistic content curation, the system maintains two independent Semantic Versioning (SemVer 2.0.0) numbers:

### 1.1 `schema_version` (Structural Semantic Version)
Describes the structural layout, field names, constraints, and validation rules of the data format.

* **Format:** `MAJOR.MINOR.PATCH` (e.g. `1.0.0`)
* **`MAJOR` increment:** Breaking changes (e.g., removing a field, renaming a required key, altering data types, changing enum values). Requires a new major schema directory (e.g. `data/schemas/2.0.0/`) and an explicit migrator.
* **`MINOR` increment:** Backward-compatible additions (e.g., adding an optional field or extending supported metadata).
* **`PATCH` increment:** Backward-compatible fixes, documentation corrections, or validator constraint refinements.

### 1.2 `dataset_version` (Content Release Version)
Describes the version of curated data contents, text pairs, activities, and annotations published in a given release.

* **Format:** `MAJOR.MINOR.PATCH` (e.g. `0.1.0`)
* **`0.1.0`:** Initial internal draft release.
* **`0.2.0`:** Expanded internal draft.
* **`1.0.0`:** First fully verified, expert-reviewed research and educational release.

> [!IMPORTANT]
> The current English MVP content remains at **`dataset_version: 0.1.0`** (internal draft) until formal expert review and licensing verifications are completed in subsequent stages.

---

## 2. Backward Compatibility & Reader Invariants

1. **Explicit Migrators:** If a record is encoded under an older supported major schema, it must pass through an explicit migrator before consumption.
2. **Unsupported Future Versions:** If a reader encounters a `schema_version` whose major version is greater than the reader's supported version, the loader must fail with an explicit `UnsupportedSchemaVersionError`.
3. **Immutability of Identifiers:** Records retain their unique identifiers across schema revisions (e.g., `C3-EN-VOC-0001`, `SIMP-EN-000001`).
4. **Extra Fields Disallowed:** Final v1 models enforce `extra="forbid"` to prevent silent schema drift.
