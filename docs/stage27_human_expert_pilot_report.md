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

## 5. Planned Expert-Authored Calibration Reference

The 10 non-locked calibration records will have canonical reference decisions authored and verified **only after ethics clearance and genuine expert involvement**:

```json
{
  "reference_status": "template_pending_human_creation",
  "calibration_manifest_hash": null,
  "reference_created_by_reviewer_id": null,
  "reference_created_by_role_required": "authorized_lead_adjudicator",
  "reference_creation_date": null,
  "historical_locked_overlap_required": 0,
  "eligible_for_human_calibration": false
}
```

### 5.1 Post-Ethics Calibration Reference Lifecycle:
1. **Authoring:** Following institutional ethics clearance, an authorized lead expert reviews the 10 calibration records and establishes reference decisions.
2. **Artifact Persistence:** Save the completed calibration artifact to disk.
3. **Cryptographic Hashing:** Calculate its genuine SHA-256 hash from the saved bytes.
4. **Metadata Recording:** Record the pseudonymous expert ID and timestamp.
5. **Secondary Verification:** Obtain independent second-person sign-off from an arbitration committee member.
6. **State Transition:** Update status to `approved_calibration_reference` to activate the calibration gate.

### 5.2 Multi-Criterion Calibration Eligibility Threshold:
The benchmark gate is termed **`pilot_calibration_eligibility_threshold`** (pilot entry qualification, not general professional certification):
* **Observed Taxonomy Concordance:** `taxonomy_exact_agreement >= 0.80` (at least 8 out of 10 exact classification matches).
* **Taxonomy Cohen's $\kappa$:** Reported descriptively. Because Cohen's $\kappa$ accounts for chance agreement and is statistically unstable over small sample sizes ($N=10$), reviewers are not failed solely because sample $\kappa$ fluctuates below $0.80$ if exact concordance is $\ge 80\%$.
* **Critical Checks:** $100\%$ concordance on predefined critical safety, answer leakage, and propositional distortion checks.
* **Ordinal Dimensions:** Quadratic weighted $\kappa_w \ge 0.75$ and mean absolute difference $\le 0.50$ across the 10 dimensions.
* **Qualitative Review:** All meaningful disagreements are discussed directly with the lead adjudicator during onboarding.

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

## 7. Inter-Rater Reliability & Stratified Bootstrap Implementation

Reliability intervals are estimated via **stratified bootstrap across complete records** (preserving paired Reviewer A and Reviewer B observations intact):

```yaml
method: stratified_bootstrap
iterations: 2000
random_seed: 42
sampling_unit: record
strata: record_type
confidence_level: 95%
numpy_version: "2.4.6"
scipy_version: "1.17.1"
agreement_module_version: "1.2.0"
implementation_hash: "4f7b0376d29938db"
```

| Measurement Dimension | Target Denominator | Reliability Metric | Target Threshold |
| :--- | :---: | :---: | :---: |
| **Independent Submissions** | 96 | Submission accounting completeness | $100\%$ accounted |
| **Taxonomy Agreement** | 48 paired records | Cohen's $\kappa$ with 95% Stratified Bootstrap CI | $\kappa \ge 0.80$ |
| **Critical Checks (Pooled)** | 480 paired checks | Pooled Cohen's $\kappa$ & % agreement | $\kappa \ge 0.80$, Concordance $\ge 90\%$ |
| **Critical Checks (Per Check)** | 48 paired records $\times 10$ | 10 individual Cohen's $\kappa$ values | No systematic blind spots |
| **Ordinal Dimensions** | 480 paired ratings | Quadratic weighted $\kappa_w$ | $\kappa_w \ge 0.75$ |
| **Composite Score Reliability** | 48 composite pairs | $\text{ICC}(A,1)$ absolute agreement single measurement | $\text{ICC}(A,1) \ge 0.80$ |
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
