# Stage 27 Real Human Expert Pilot Report (Protocol & Execution Staging)
**Dataset Expansion & Validation — Component 3 (AI & NLP Based Language Simplification for Children Aged 4–8)**

---

## 1. Current Milestone Status

```yaml
stage_27_infrastructure: COMPLETE
operational_simulation: COMPLETE
human_expert_pilot: PENDING ETHICS CLEARANCE
full_human_expert_review: NOT STARTED
expert_reviewed_release_0.3.0: BLOCKED
stage_27_overall: IN PROGRESS
```

> [!CAUTION]
> **Production Publication Lock:**
> Release 0.3.0 publication remains strictly blocked (`RELEASE_BLOCKED_INCOMPLETE_EXPERT_REVIEW`). Human expert data collection will commence only following confirmation of institutional ethics clearance.

---

## 2. Institutional Ethics & Regulatory Gate (Prerequisite)

Before enrolling candidate reviewers:
1. **Human Research Participant Requirement:** Soliciting professional evaluations, time, feedback, and credential declarations from educators, linguists, or speech-language pathologists constitutes human participant research.
2. **Review Prerequisite:** Formal protocol review and written clearance/amendment approval must be confirmed with the institutional supervisory committee and University Institutional Review Board (IRB) / Ethics Committee.
3. **Strict Gate:** No live human participant accounts will be activated until ethical authorization is documented.

---

## 3. Reviewer Panel Eligibility & Preferred Experience

To avoid unnecessary recruitment bottlenecks while ensuring clinical and pedagogical validity, eligibility criteria separate **mandatory competence** from **preferred experience**:

### 3.1 Mandatory Requirements
* **Professional Qualification:** Recognized degree in Primary Education, Early Childhood Development, Speech-Language Therapy/Pathology, Applied Linguistics, or NLP/Computational Linguistics.
* **Role Relevance:** Active or prior professional experience teaching, evaluating, or delivering speech therapy to young learners (aged 4–8) or developing clinical language simplification systems.
* **Documented Competency:** Passing the non-locked benchmark calibration gate.
* **Ethics Compliance:** Signed informed consent, confidentiality agreement, and zero declared conflicts of interest with Stage 20 authoring or Stage 26/28 model pipelines.

### 3.2 Preferred Experience (Non-Exclusionary)
* **Reviewer A (Primary Education / Literacy):** Preferred $7+$ years in primary language instruction.
* **Reviewer B (Early Childhood / Linguistics):** Preferred $5+$ years in child developmental linguistics.
* **Lead Adjudicator:** Preferred $12+$ years in pediatric language pathology or senior editorial arbitration.
* **Accessibility Specialist:** Certified Speech-Language Therapist / Pathologist (SLT/SLP) for DLD-specific evaluations.

---

## 4. Protected De-Identification & Privacy Protocol

Public repository documentation strictly excludes all Personally Identifiable Information (PII) including names, institutional affiliations, personal emails, phone numbers, and physical signatures. Public records expose only anonymized tokens:

```json
{
  "reviewer_id": "REV-001",
  "qualification_category": "early_childhood_education",
  "authorized_dimensions": [
    "age_appropriateness",
    "instruction_clarity"
  ],
  "qualification_verified": true,
  "consent_recorded": true,
  "coi_status": "none_declared"
}
```

---

## 5. Pre-Established Calibration Gold Reference

The 10 non-locked calibration records must have ground-truth benchmark decisions established **prior** to candidate reviewer onboarding:

```json
{
  "calibration_manifest_hash": "sha256:7f8e3d2c1b0a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4e",
  "reference_created_by_role": "Lead Adjudicator / Pediatric Language Consultant",
  "reference_creation_date": "2026-10-10",
  "reference_rationale": "Standardized canonical taxonomy, ordinal rating anchors, and critical flag definitions established independently by the lead arbitration committee without consulting locked evaluation sets.",
  "historical_locked_overlap": 0
}
```

### Calibration Eligibility Threshold:
The benchmark gate is termed **`pilot_calibration_eligibility_threshold`** (not general professional certification):
$$\text{Composite Score} = 0.35 \times \kappa_{\text{taxonomy}} + 0.35 \times \text{Concordance}_{\text{critical}} + 0.30 \times \kappa_{w,\text{ordinal}} \ge \mathbf{0.80}$$
* **Taxonomy:** Minimum 8/10 matches ($\kappa \ge 0.80$).
* **Critical Checks:** $100\%$ concordance on safety, answer leakage, and meaning preservation flags.
* **Ordinal Dimensions:** Quadratic weighted $\kappa_w \ge 0.75$ and mean absolute difference $\le 0.50$.

---

## 6. Real Human Pilot Execution (48 Records $\times$ 2 = 96 Submissions)

The frozen stratified pilot sample comprises:
* **32 text simplification pairs**
* **10 lexicon entries**
* **6 adaptation activities**
* Systematic representation of syntactic, lexical, and structural reformulation candidates.

### Strict Mode Isolation Guard:
To prevent any possibility of synthetic data contaminating human evaluations, the execution pipeline enforces:
```python
assert all(
    submission.review_mode == "real_human_expert_review"
    and submission.submission_origin == "human_entered"
    for submission in expert_evaluation_inputs
), "Contamination detected: Non-human or simulated submissions found in expert evaluation inputs"
```

Each submission must record:
```yaml
submission_origin: human_entered
review_mode: real_human_expert_review
authenticated_reviewer_id: "REV-001"
assignment_id: "ASG-..."
submitted_at: "2026-..."
rubric_version: "1.1-frozen"
record_hash: "sha256:..."
submission_hash: "sha256:..."
is_sealed: true
```

---

## 7. Inter-Rater Reliability Accounting Plan

Upon completion of the 96 human submissions, agreement will be reported across the verified denominators:

| Measurement Dimension | Target Denominator | Reliability Metric | Target Threshold |
| :--- | :---: | :---: | :---: |
| **Independent Submissions** | 96 | Submission accounting completeness | $100\%$ accounted |
| **Taxonomy Agreement** | 48 paired records | Cohen's $\kappa$ with 95% Wald CI | $\kappa \ge 0.80$ |
| **Critical Checks (Pooled)** | 480 paired checks | Pooled Cohen's $\kappa$ & % agreement | $\kappa \ge 0.80$, Concordance $\ge 90\%$ |
| **Critical Checks (Per Check)** | 48 paired records $\times 10$ | 10 individual Cohen's $\kappa$ values | No systematic blind spots |
| **Ordinal Dimensions** | 480 paired ratings | Quadratic weighted $\kappa_w$ | $\kappa_w \ge 0.75$ |
| **Composite Score Reliability** | 48 composite pairs | $\text{ICC}(A,1)$ absolute agreement | $\text{ICC}(A,1) \ge 0.80$ |
| **Corpus-Wide Reliability** | 48 records | Krippendorff's $\alpha$ with bootstrap CI | $\alpha \ge 0.80$ |

---

## 8. Protected Provenance Statement Template

Upon completion and sealing of all human submissions and adjudications, the final provenance declaration will be generated:

```json
{
  "pilot_review_mode": "real_human_expert_review",
  "pilot_records": 48,
  "independent_human_submissions": 96,
  "script_generated_submissions": 0,
  "llm_generated_submissions": 0,
  "reviewers_verified": true,
  "consent_recorded": true,
  "rubric_version": "1.1-frozen",
  "historical_locked_set_used_for_calibration": false
}
```
