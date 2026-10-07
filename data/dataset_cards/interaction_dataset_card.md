# Dataset Card: Interaction Dataset (English MVP)

## 1. Summary
The **Interaction Dataset** governs learner attempt evidence, response transcripts, response timing, and support escalation outcomes generated during runtime educational activities.

- **Schema Version:** `1.0.0`
- **Dataset Content Version:** `0.1.0`
- **JSON Schemas:** `data/schemas/1.0.0/interaction_record.schema.json`, `data/schemas/1.0.0/interaction_export.schema.json`

## 2. Governance & Ownership Boundaries
- **Operational Source of Truth:** Component 3 Relational Database (SQLAlchemy SQLite `ActivitySession`, `Attempt`, `TaskResult`).
- **Longitudinal Analytics Owner:** Component 4 (Longitudinal Learner Analytics & Reporting).
- **Component 3 Scope:** Component 3 captures interaction records during sessions and computes `local_preliminary_trend` indicators for real-time scaffolding.
- **Privacy Classification:** `private_learner_evidence`.
- **Licence:** `project-internal` (restrictive defaults).

## 3. Storage & Privacy Safeguards
- **Storage Rules:** Private interaction records and de-identified snapshots reside in `data/interaction_dataset/private/` and `data/interaction_dataset/deidentified_exports/`.
- **Git Protection:** Strictly ignored by `.gitignore`. Must never be committed to Git.
- **Pseudonymization:** Real child identities are pseudonymous (`CHILD-XXX`, `PSEUDO-XXX`).
- **Export Auditing:** Any snapshot export triggers an immutable `IntegrationEvent` audit entry in the database.
- **De-Identified Export Allowlist:** Filtered through `DeidentifiedInteractionExportV1` to guarantee raw responses are excluded.
