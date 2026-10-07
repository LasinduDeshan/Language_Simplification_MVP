# Stage 15 Manual Review and Triage Policy

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Document Version:** 1.0.0  

---

## 1. Scope of Stage 15 Triage

Stage 15 establishes an operational **Manual Review Queue** and **Record Correction Service** to triage records flagged by automated validators.

### Strict Governance Boundary: Stage 15 vs. Stage 16

| Action / Operation | Stage 15 Permitted? | Stage 16 Permitted? | Notes |
| :--- | :---: | :---: | :--- |
| **`acknowledge_finding`** | ✅ Yes | ✅ Yes | Confirms reviewer has seen the flag. |
| **`mark_false_positive`** | ✅ Yes | ✅ Yes | Notes validator inaccuracy with justification. |
| **`submit_correction`** | ✅ Yes | ✅ Yes | Creates immutable `RecordRevision` draft. |
| **`request_expert_review`** | ✅ Yes | ✅ Yes | Escalates record to Stage 16 domain queue. |
| **`revalidate`** | ✅ Yes | ✅ Yes | Re-runs validators against new revision. |
| **`approved`** | ❌ **FORBIDDEN** | ✅ Yes | Reserved for Stage 16 expert governance. |
| **`expert_reviewed`** | ❌ **FORBIDDEN** | ✅ Yes | Reserved for Stage 16 expert governance. |
| **`approved_for_child_delivery`** | ❌ **FORBIDDEN** | ✅ Yes | Reserved for Stage 16 clinical/pedagogical review. |
| **`research_eligible`** | ❌ **FORBIDDEN** | ✅ Yes | Reserved for Stage 16 licensing & provenance sign-off. |

---

## 2. Review Queue Priority Levels

Review queue entries are prioritized automatically based on triggering rule severity:

1. **`urgent`**: Quarantined records (safety/privacy/leakage concern). Must be addressed prior to any export.
2. **`high`**: Blocking error rules on adaptation tasks or core meaning preservation.
3. **`medium`**: Syntactic, complexity, or lexical warnings.
4. **`low`**: Minor formatting or informational observations.

---

## 3. Non-Destructive Revision Tracking

When a correction is submitted via the `CorrectionService`:
1. The original record remains unchanged.
2. A new `RecordRevision` is created with:
   - `revision_id` (e.g. `REV-HIST-000001`)
   - `parent_revision_id`
   - `previous_content` (snapshot)
   - `corrected_content` (new snapshot)
   - `change_reason`
   - `created_by` (reviewer ID)
   - `created_at` (timestamp)
3. Revalidation creates an updated `RecordQualitySummary` linked to the new revision.
