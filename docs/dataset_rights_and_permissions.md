# Dataset Rights, Provenance & Privacy Governance Guidance

**Component:** Component 3 — AI/NLP-Based Personalized Language Simplification  
**Scope:** Reusable NLP resources, test activities, text pairs, interaction snapshots

---

## 1. Provenance Requirements

Every reusable record in the Adaptation Test Set, Simplification Corpus, and Lexicon Repository must document its complete lineage:

1. **`source_type`:** Origin category:
   - `team_authored`: Created by the engineering or research team for MVP validation.
   - `expert_authored`: Authored by a verified speech-language pathologist or educator.
   - `open_licence`: Ingested from an open, permissively licensed external dataset.
   - `permission_granted`: Obtained through explicit written permission.
   - `generated`: Produced by an AI/NLP model or rule-based pipeline.
   - `interaction_derived`: Anonymized derivative of learner interaction logs.
2. **`source_name`:** Formal name of the source or authoring entity.
3. **`source_record_id`:** Identifier in the original upstream source system or file.
4. **`created_by_role`:** Creator's functional role (`project_team`, `linguist`, `speech_language_pathologist`, `system`).

---

## 2. Default-Restrictive Rights Framework

Unknown or unverified rights automatically default to the most restrictive state:

| Field | Default Value | Rule / Invariant |
|---|---|---|
| `licence_id` | `project-internal` | Cannot be treated as open-source without explicit verification |
| `redistribution_allowed` | `false` | Must never be distributed in public repositories without verified licence |
| `commercial_use_allowed` | `false` | Cannot be used commercially without IP clearance |
| `external_api_processing_allowed` | `false` | **Strict LLM Gating:** Record cannot be sent to third-party commercial LLMs unless explicitly true |
| `research_eligible` | `false` | Cannot be included in research datasets without formal assessment |
| `approved_for_child_delivery` | `false` | Cannot be presented to children without `validation_status="approved"` |

---

## 3. Privacy & Interaction Data Safeguards

1. **Database as Operational Source of Truth:** Relational DB SQLite (`adaptive_learning.db`) stores operational records.
2. **Private File Exclusions:** Local interaction snapshot files live under `data/interaction_dataset/private/` and are strictly ignored by Git.
3. **De-Identified Export Allowlist:** Exported data for Component 4 or research analytics must pass through an explicit allowlist schema (`DeidentifiedInteractionExportV1`) that strips raw transcriptions, free-text notes, and authentication identifiers.
4. **Consent Gating:** Consent metadata (`status`, `reference_id`, `verified_at`) must be recorded.
