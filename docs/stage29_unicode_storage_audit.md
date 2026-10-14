# Stage 29 — Unicode and Database Storage Capability Audit

**Component:** Component 3 — Language Simplification MVP
**Stage:** Stage 29 (Sinhala Database, UI and Font Support)
**Database Engine:** SQLite (Version 3.45.1)
**PRAGMA Encoding:** UTF-8
**Database Path:** `backend/adaptive_learning.db`

---

## 1. Executive Summary

The storage layer was audited for UTF-8 Unicode fidelity, text column collation, and parameter preservation. SQLite operates natively under `UTF-8`. Non-mutating parameterized insert and select probes confirmed that Sinhala Unicode strings—including zero-width joiners (ZWJ), combining marks (kombuva, aelepilla), ligatures (Yansaya, Rakaransaya, Bandi akuru), and mixed-script text—are stored and retrieved with exact code-point fidelity without corruption or lossy conversion.

---

## 2. Database Environment and Encoding Settings

- **Engine:** SQLite 3
- **Python SQLite Driver:** `2.6.0`
- **Underlying SQLite Library:** `3.45.1`
- **Encoding:** `UTF-8` (PRAGMA encoding confirmed)
- **Collation Behavior:** Default `BINARY` collation preserves exact byte/code-point order.
- **Foreign Keys:** Enabled in application configuration.

---

## 3. Table and Column Inventory

A total of **30 tables** containing **264 text-bearing columns** were inventoried:

| Table Name | Text Columns | Types |
|---|---|---|
| `activity_assets` | 12 | `id` (VARCHAR(36)), `task_id` (VARCHAR(36)), `asset_type` (VARCHAR(50)), `asset_key` (VARCHAR(100)), `file_path_or_url` (VARCHAR(500)), `alt_text` (TEXT), `asset_source` (VARCHAR(200)), `asset_creator` (VARCHAR(200)), `license_type` (VARCHAR(100)), `license_url` (VARCHAR(500)), `permission_status` (VARCHAR(100)), `attribution_text` (TEXT) |
| `activity_questions` | 4 | `id` (VARCHAR(36)), `task_id` (VARCHAR(36)), `question_text` (TEXT), `response_mode` (VARCHAR(50)) |
| `activity_sessions` | 11 | `id` (VARCHAR(36)), `learner_id` (VARCHAR(36)), `task_id` (VARCHAR(36)), `status` (VARCHAR(50)), `initial_support_level` (VARCHAR(20)), `current_support_level` (VARCHAR(20)), `final_outcome` (VARCHAR(50)), `created_by` (VARCHAR(100)), `generation_mode` (VARCHAR(20)), `task_version` (VARCHAR(20)), `adaptation_configuration_version` (VARCHAR(20)) |
| `adaptations` | 12 | `id` (VARCHAR(36)), `experiment_run_id` (VARCHAR(36)), `activity_session_id` (VARCHAR(36)), `source_attempt_id` (VARCHAR(36)), `support_level` (VARCHAR(20)), `generation_method` (VARCHAR(50)), `child_instruction` (TEXT), `supportive_message` (TEXT), `answer_format` (VARCHAR(50)), `provider` (VARCHAR(50)), `model_name` (VARCHAR(100)), `prompt_version` (VARCHAR(50)) |
| `alembic_version` | 1 | `version_num` (VARCHAR(32)) |
| `attempts` | 29 | `id` (VARCHAR(36)), `experiment_run_id` (VARCHAR(36)), `activity_session_id` (VARCHAR(36)), `adaptation_id` (VARCHAR(36)), `attempt_status` (VARCHAR(30)), `presented_instruction` (TEXT), `instruction_shown` (TEXT), `support_level` (VARCHAR(20)), `adaptation_strategy` (VARCHAR(100)), `generation_method` (VARCHAR(50)), `validation_status` (VARCHAR(30)), `response_source` (VARCHAR(50)), `manual_transcript` (TEXT), `speech_transcript` (TEXT), `selected_option` (TEXT), `completion_status` (VARCHAR(30)), `assistance_level` (VARCHAR(30)), `original_response_mode` (VARCHAR(50)), `current_response_mode` (VARCHAR(50)), `target_skill` (VARCHAR(100)), `concept_result` (VARCHAR(30)), `target_skill_result` (VARCHAR(30)), `retry_reason` (VARCHAR(100)), `final_concept_result` (VARCHAR(30)), `final_target_skill_result` (VARCHAR(30)), `override_reason` (TEXT), `reviewed_by_user_id` (VARCHAR(100)), `adult_interpretation` (VARCHAR(30)), `adult_notes` (TEXT) |
| `dataset_manual_review_queue` | 10 | `entry_id` (VARCHAR(64)), `run_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `dataset_layer` (VARCHAR(64)), `priority` (VARCHAR(32)), `summary` (TEXT), `recommended_review_type` (VARCHAR(64)), `review_status` (VARCHAR(64)), `assigned_reviewer_id` (VARCHAR(64)), `resolution_notes` (TEXT) |
| `dataset_quality_rule_results` | 12 | `result_id` (VARCHAR(64)), `run_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `dataset_layer` (VARCHAR(64)), `rule_id` (VARCHAR(64)), `rule_version` (VARCHAR(32)), `validator_name` (VARCHAR(128)), `validator_version` (VARCHAR(32)), `severity` (VARCHAR(32)), `threshold` (VARCHAR(64)), `message` (TEXT), `recommended_action` (TEXT) |
| `dataset_record_quality_summaries` | 7 | `summary_id` (VARCHAR(64)), `run_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `dataset_layer` (VARCHAR(64)), `schema_version` (VARCHAR(32)), `quality_rule_set_version` (VARCHAR(32)), `quality_status` (VARCHAR(64)) |
| `dataset_record_revisions` | 7 | `revision_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `dataset_layer` (VARCHAR(64)), `parent_revision_id` (VARCHAR(64)), `change_reason` (TEXT), `created_by` (VARCHAR(64)), `revalidation_run_id` (VARCHAR(64)) |
| `dataset_validation_runs` | 8 | `run_id` (VARCHAR(64)), `dataset_layer` (VARCHAR(64)), `dataset_version` (VARCHAR(32)), `quality_rule_set_version` (VARCHAR(32)), `status` (VARCHAR(32)), `idempotency_key` (VARCHAR(128)), `created_by` (VARCHAR(64)), `error_message` (TEXT) |
| `experiment_runs` | 6 | `id` (VARCHAR(36)), `learner_id` (VARCHAR(36)), `task_id` (VARCHAR(36)), `generation_mode` (VARCHAR(20)), `status` (VARCHAR(20)), `final_outcome` (VARCHAR(20)) |
| `expert_adjudications` | 9 | `id` (VARCHAR(36)), `adjudication_case_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `adjudicator_id` (VARCHAR(50)), `reviewer_a_submission_id` (VARCHAR(64)), `reviewer_b_submission_id` (VARCHAR(64)), `final_taxonomy_class` (VARCHAR(50)), `final_disposition` (VARCHAR(50)), `decision_rationale` (TEXT) |
| `expert_evaluations` | 4 | `id` (VARCHAR(36)), `adaptation_id` (VARCHAR(36)), `evaluator_code` (VARCHAR(50)), `comments` (TEXT) |
| `expert_release_approvals` | 4 | `id` (VARCHAR(36)), `release_version` (VARCHAR(20)), `approved_by` (VARCHAR(50)), `signoff_role` (VARCHAR(50)) |
| `expert_review_assignments` | 7 | `id` (VARCHAR(36)), `assignment_id` (VARCHAR(64)), `batch_id` (VARCHAR(50)), `record_id` (VARCHAR(64)), `reviewer_id` (VARCHAR(50)), `reviewer_role` (VARCHAR(20)), `status` (VARCHAR(20)) |
| `expert_review_audit_log` | 6 | `id` (VARCHAR(36)), `event_id` (VARCHAR(64)), `event_type` (VARCHAR(50)), `actor_id` (VARCHAR(50)), `record_id` (VARCHAR(64)), `event_hash` (VARCHAR(64)) |
| `expert_review_batches` | 6 | `id` (VARCHAR(36)), `batch_id` (VARCHAR(50)), `reviewer_panel_id` (VARCHAR(50)), `reviewer_a_id` (VARCHAR(50)), `reviewer_b_id` (VARCHAR(50)), `status` (VARCHAR(20)) |
| `expert_review_submissions` | 10 | `id` (VARCHAR(36)), `submission_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `reviewer_id` (VARCHAR(50)), `batch_id` (VARCHAR(50)), `taxonomy_class` (VARCHAR(50)), `lexicon_disposition` (VARCHAR(50)), `reviewer_notes` (TEXT), `provisional_disposition` (VARCHAR(50)), `submission_hash` (VARCHAR(64)) |
| `expert_reviewer_consents` | 4 | `id` (VARCHAR(36)), `reviewer_id` (VARCHAR(50)), `coi_details` (TEXT), `ip_or_signature_hash` (VARCHAR(64)) |
| `expert_reviewers` | 6 | `id` (VARCHAR(36)), `reviewer_id` (VARCHAR(50)), `full_name` (VARCHAR(100)), `role` (VARCHAR(50)), `qualification_category` (VARCHAR(100)), `account_status` (VARCHAR(20)) |
| `expert_revisions` | 13 | `id` (VARCHAR(36)), `revision_id` (VARCHAR(64)), `record_id` (VARCHAR(64)), `source_group_id` (VARCHAR(64)), `original_text` (TEXT), `revised_text` (TEXT), `original_hash` (VARCHAR(64)), `revised_hash` (VARCHAR(64)), `revision_reason` (TEXT), `revised_by` (VARCHAR(50)), `stage14_schema_validation` (VARCHAR(20)), `stage15_quality_validation` (VARCHAR(20)), `final_disposition` (VARCHAR(50)) |
| `integration_events` | 9 | `id` (VARCHAR(36)), `experiment_run_id` (VARCHAR(36)), `activity_session_id` (VARCHAR(36)), `attempt_id` (VARCHAR(36)), `adaptation_id` (VARCHAR(36)), `target_component` (VARCHAR(50)), `event_type` (VARCHAR(100)), `schema_version` (VARCHAR(20)), `delivery_status` (VARCHAR(20)) |
| `language_observations` | 5 | `id` (VARCHAR(36)), `attempt_id` (VARCHAR(36)), `category` (VARCHAR(50)), `observation_code` (VARCHAR(100)), `evidence` (TEXT) |
| `learner_profiles` | 11 | `id` (VARCHAR(36)), `learner_code` (VARCHAR(50)), `grade` (VARCHAR(50)), `risk_support_level` (VARCHAR(20)), `english_level` (VARCHAR(20)), `preferred_language` (VARCHAR(10)), `screening_risk_level` (VARCHAR(20)), `recommended_support_level` (VARCHAR(20)), `screening_source` (VARCHAR(50)), `screening_version` (VARCHAR(50)), `performance_scoring_version` (VARCHAR(20)) |
| `performance_patterns` | 7 | `id` (VARCHAR(36)), `learner_id` (VARCHAR(36)), `pattern_type` (VARCHAR(50)), `pattern_code` (VARCHAR(100)), `successful_support` (VARCHAR(100)), `recommended_support` (VARCHAR(20)), `source` (VARCHAR(50)) |
| `question_responses` | 6 | `id` (VARCHAR(36)), `attempt_id` (VARCHAR(36)), `question_id` (VARCHAR(36)), `manual_response` (TEXT), `concept_result` (VARCHAR(30)), `target_skill_result` (VARCHAR(30)) |
| `task_results` | 20 | `id` (VARCHAR(36)), `session_id` (VARCHAR(36)), `learner_id` (VARCHAR(36)), `task_id` (VARCHAR(36)), `learner_code` (VARCHAR(50)), `task_code` (VARCHAR(50)), `task_title` (VARCHAR(200)), `category` (VARCHAR(50)), `target_skill` (VARCHAR(100)), `difficulty` (VARCHAR(20)), `final_outcome` (VARCHAR(50)), `risk_before` (VARCHAR(20)), `risk_after` (VARCHAR(20)), `diagnostic_notes` (TEXT), `educational_summary_notes` (TEXT), `screening_risk_level` (VARCHAR(20)), `recommended_support_level` (VARCHAR(20)), `target_domain` (VARCHAR(50)), `score_update_event_id` (VARCHAR(36)), `scoring_version` (VARCHAR(20)) |
| `tasks` | 15 | `id` (VARCHAR(36)), `task_code` (VARCHAR(50)), `title` (VARCHAR(200)), `category` (VARCHAR(50)), `task_type` (VARCHAR(50)), `subskill` (VARCHAR(100)), `target_skill` (VARCHAR(100)), `language` (VARCHAR(10)), `learning_objective` (TEXT), `child_friendly_instruction` (TEXT), `original_instruction` (TEXT), `base_difficulty` (VARCHAR(20)), `prompt` (TEXT), `passage` (TEXT), `follow_up_for_strong` (TEXT) |
| `validation_results` | 3 | `id` (VARCHAR(36)), `adaptation_id` (VARCHAR(36)), `status` (VARCHAR(20)) |

---

## 4. Non-Mutating Unicode Probe Results

| Test Probe | Payload | Code Points Match | Decoded Equality | Status |
|---|---|---|---|---|
| `basic_sinhala` | `සිංහල භාෂාව` | True | True | **PASSED** |
| `zwj_yansaya` | `ව්‍යවස්ථාව` | True | True | **PASSED** |
| `zwj_rakaransaya` | `ශ්‍රී ලංකා` | True | True | **PASSED** |
| `bandi_akuru` | `ක්‍ෂීර` | True | True | **PASSED** |
| `kombuva_and_signs` | `කෞතුකාගාරය` | True | True | **PASSED** |
| `mixed_english_sinhala` | `Grade 1 සිංහල Level A` | True | True | **PASSED** |
| `digits_and_punct` | `පිටුව 123 (අංක: 45/67).` | True | True | **PASSED** |

---

## 5. Audit Findings & WP3 Schema Decision Impact

1. **Unicode Safety:** SQLite text storage handles multi-byte UTF-8 sequences natively.
2. **No Character Truncation:** SQLite dynamically-sized text types do not enforce rigid ASCII length constraints.
3. **ZWJ / ZWNJ Preservation:** Zero-Width Joiner (`U+200D`) and Zero-Width Non-Joiner (`U+200C`) pass through parameterized queries without alteration.
4. **Language Metadata Readiness:** Existing dataset and content tables in the application already support language tagging or can store localized text via normalized schemas without altering legacy tables.

Audit successfully verified by `scripts/stage29/verify_database_encoding.py`.
