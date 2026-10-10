# Stage 27 Operational Simulated Pilot Report
**Dataset Expansion & Validation — Component 3 (AI & NLP Based Language Simplification for Children Aged 4–8)**

---

## 1. Executive Summary & Provenance Disclosure

This document records the empirical results of the **Stage 27 Operational Software Simulation Pilot**. The objective of this pilot was to validate system throughput, database constraints, append-only triggers, cross-reviewer blinding, conflict detection, and statistical agreement calculations.

> [!IMPORTANT]
> **Operational Simulation Classification:**
> The ratings in this pilot were generated via automated software simulation ([`backend/app/datasets/expert_review/pilot_runner.py`](file:///c:/Users/Lasindu/Documents/GitHub/Language_Simplification_MVP/backend/app/datasets/expert_review/pilot_runner.py)) simulating realistic reviewer distributions. These submissions do **not** constitute empirical human evidence.
> 
> ```yaml
> pilot_review_mode: operational_simulation
> human_expert_evidence: false
> ```

### 1.1 Verified Submission Origins ($N=96$)
```json
{
  "pilot_review_mode": "operational_simulation",
  "human_expert_evidence": false,
  "submission_origins": {
    "human_entered": 0,
    "script_generated": 96,
    "fixture_generated": 0,
    "llm_generated": 0,
    "unknown_origin": 0
  }
}
```

---

## 2. Statistical Denominators & Measurement Accounting

For 48 pilot records, two independent reviewer pathways, and 10 evaluation dimensions/checks, the exact measurement accounting is defined as follows:

| Measurement Dimension | Correct Accounting | Mathematical Basis | Description |
| :--- | :---: | :---: | :--- |
| **Independent Submissions** | **96** | $48 \times 2$ | Total sealed review payloads submitted to the system |
| **Taxonomy Paired Observations** | **48** | 48 records | Paired classification decisions for Cohen's $\kappa$ |
| **Critical-Check Paired Observations** | **480** | $48 \times 10$ | Total paired binary decisions across 10 safety/integrity checks |
| **Critical-Check Individual Decisions** | **960** | $48 \times 10 \times 2$ | Individual check evaluations logged across both reviewers |
| **Ordinal Paired Dimension Ratings** | **480** | $48 \times 10$ | Paired 1–5 ratings across 10 evaluation dimensions |
| **Ordinal Individual Ratings** | **960** | $48 \times 10 \times 2$ | Total individual dimension ratings recorded |
| **Composite-Score Pairs for ICC** | **48** | 48 records | Mean item score pairs evaluated between Reviewer A and Reviewer B |

---

## 3. Reviewer Isolation & Blinding Architecture

To maintain methodological rigor, the system implements **Independent Blinded Review with Cross-Reviewer Isolation**:
* **Cross-Reviewer Blinding:** Reviewer A and Reviewer B operate in separate authenticated sessions and cannot inspect peer submissions, scores, or rationales.
* **Model Blinding:** Reviewers are blinded to pipeline architecture, model identity, prompting techniques, and generation metadata.
* **Split & Metric Blinding:** Reviewers have no access to algorithmic NLP metrics (SARI, BLEU, FKGL, BERTScore) or dataset split designations (train/val/test).
* **Administrative Isolation:** System administrators are cryptographically and structurally blocked from entering or modifying reviews on behalf of reviewers.

---

## 4. Intraclass Correlation Coefficient (ICC) Specification

Reliability across ordinal quality dimensions is computed using **absolute agreement**, rather than consistency, to ensure reviewers assign similar actual scores rather than merely preserving rank order.

```yaml
icc_model: two-way mixed-effects
icc_type: absolute agreement
icc_unit: single measurement
icc_form: ICC(A,1)
icc_function: calculate_icc_a1
numpy_version: "2.4.6"
scipy_version: "1.17.1"
agreement_module_version: "1.2.0"
implementation_hash: "4f7b0376d29938db"
```

### Statistical Formulation:
Following McGraw & Wong (1996, Case 3A) and Shrout & Fleiss (1979):
$$\text{ICC}(A, 1) = \frac{MS_{\text{items}} - MS_{\text{error}}}{MS_{\text{items}} + (k - 1) MS_{\text{error}} + \frac{k}{n} (MS_{\text{raters}} - MS_{\text{error}})}$$

*Methodological Note:* Consistency $\text{ICC}(3,1)$ ignores between-rater mean square ($MS_{\text{raters}}$), meaning it would yield 1.0 even if Reviewer B consistently scored 1 point higher than Reviewer A across every item. $\text{ICC}(A,1)$ explicitly incorporates $MS_{\text{raters}}$, penalizing systematic scoring shifts and enforcing strict calibration.

---

## 5. Reliability Results & Stratified Bootstrap Specification

Confidence intervals are calculated using **stratified bootstrap across complete records** (2,000 iterations, random seed 42, stratified by record type, sampling complete pairs):

| Metric | Target | Simulated Value | Denominator ($N$) | 95% Stratified Bootstrap CI |
| :--- | :---: | :---: | :---: | :---: |
| **Taxonomy Cohen's $\kappa$** | $\ge 0.80$ | **0.88** | 48 paired records | $[0.74, 1.00]$ |
| **Critical Checks (Pooled)** | $\ge 0.80$ | **0.95** | 480 paired checks | $[0.91, 0.99]$ |
| **Critical Checks (Record-Level Any-Failure)** | $\ge 0.80$ | **0.91** | 48 paired records | $[0.78, 1.00]$ |
| **Meaning Preservation Quadratic $\kappa_w$** | $\ge 0.75$ | **0.84** | 48 paired ratings | $[0.71, 0.97]$ |
| **Age Appropriateness Quadratic $\kappa_w$** | $\ge 0.75$ | **0.82** | 48 paired ratings | $[0.68, 0.96]$ |
| **Ordinal Quality $\text{ICC}(A,1)$** | $\ge 0.80$ | **0.83** | 48 composite pairs | $[0.71, 0.95]$ |
| **Krippendorff's $\alpha$ (Nominal)** | $\ge 0.80$ | **0.87** | 48 items | $[0.75, 0.99]$ |

### 5.1 Per-Check Critical Flag Kappas ($N=48$ each)
Each of the 10 critical failure flags was evaluated independently:
1. `meaning_changed`: $\kappa = 0.94$
2. `important_information_removed`: $\kappa = 0.91$
3. `unsupported_information_added`: $\kappa = 0.96$
4. `negation_changed`: $\kappa = 1.00$
5. `quantity_or_number_changed`: $\kappa = 1.00$
6. `entity_changed`: $\kappa = 0.95$
7. `spatial_relation_changed`: $\kappa = 1.00$
8. `temporal_or_action_order_changed`: $\kappa = 0.92$
9. `answer_leakage_detected`: $\kappa = 1.00$
10. `unsafe_or_inappropriate_content`: $\kappa = 1.00$

---

## 6. Workload & Velocity Reconciliation

Based on the simulated pilot pacing:
* **Average Review Velocity:** $1.73\text{ minutes per submission}$ ($103.8\text{ seconds}$).
* **Full Production Corpus:** 1,632 remaining records $\times 2 = 3,264$ independent submissions.

### Workload Breakdown:
$$\text{Direct Independent Review} = 3,264 \times 1.73\text{ min} = 5,646.72\text{ min} = \mathbf{94.1\text{ hours}}$$

* **Direct Independent Review:** $94.1\text{ reviewer-hours}$
* **Expected Adjudication:** $7.9\text{ arbiter-hours}$ (projected on 16.7% divergence rate)
* **Revision & Re-Review:** $3.5\text{ hours}$
* **Administrative & Session Auditing:** $3.3\text{ hours}$
* **Total Projected Human Effort:** $\mathbf{108.8\text{ hours}}$

---

## 7. Technical Infrastructure Verification

- [x] **Alembic Migrations:** 9 persistent relational tables created with schema idempotency.
- [x] **Database Triggers:** 11 database-level triggers aborting SQL `UPDATE` and `DELETE` on sealed submissions, audit logs, and adjudications.
- [x] **Distinct Reviewer Isolation:** SQLite `CHECK(reviewer_a_id != reviewer_b_id)` and assignment-level validation enforced.
- [x] **Simulation vs Human Isolation:** Strict mode enforcement preventing simulated records from being processed in human evaluation runs.
- [x] **Regression Suite:** 45 / 45 expert review unit and integration tests passing.
