# Stage 34 — Ethics, Privacy, and Reviewer Governance Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Stage:** Stage 34 — Sinhala Expert Linguistic and Child-Development Validation  
**Status:** Approved Readiness Protocol — WP1 Complete  
**Prerequisite Baseline:** `stage-33-complete-v2` (`74481f4d09beeba42ccb9b9c32ff994e372af5bf`)  
**Start Tag:** `stage-34-start`

---

## 1. Institutional Ethics and Governance Determination

### 1.1 Scope and Determination

Stage 34 evaluates the controlled simplification rules, lexicons, and draft synthetic candidate texts developed during Stages 30 through 33 for the Sinhala language. The evaluation is conducted entirely through human expert linguistic analysis, pedagogical review, and developmental appropriateness assessment.

**Formal Determination:**
- **Activity Classification:** Expert panel linguistic and professional educational assessment of algorithmically simplified text candidates.
- **Human Subjects Status:** The participants are consenting adult subject-matter experts (linguists, primary educators, child-development specialists, and adjudicators) evaluating textual materials in an evaluative/expert capacity. No children, students, or patients participate.
- **Institutional Determination Reference:** `ETH-S34-EXPERT-EVAL-2026-01` (Institutional Research Compliance Office — Expert Panel Assessment Exemption).
- **Clinical Boundary:** This stage does **not** evaluate diagnostic effectiveness, does not involve individuals with Developmental Language Disorder (DLD), and does not authorize or perform clinical interventions or child delivery.

---

## 2. Reviewer Consent, Obligations, and Compensation

### 2.1 Consent Protocol

Before recruitment and onboarding, every expert reviewer must review and digitally sign the standardized consent instrument:
- **Consent Document ID:** `S34-CONSENT-V1`
- **Consent Hash (SHA-256):** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (standard frozen template hash)

The consent terms explicitly cover:
1. **Purpose:** Academic and algorithmic quality validation of text simplification models;
2. **Voluntary Participation:** The right to withdraw at any stage prior to batch submission without penalty or loss of compensation;
3. **Confidentiality:** Strict non-disclosure of restricted source texts and candidates;
4. **Data Privacy:** Pseudonymization of reviewer identities;
5. **Conflict of Interest:** Mandatory disclosure of conflicts regarding text sources or algorithm authorship;
6. **Compensation:** Fair honoraria based on declared professional rates and estimated annotation workload;
7. **Complaints and Escalation:** Designated institutional compliance contact.

---

## 3. Child Safeguarding Boundary

Stage 34 is strictly **expert-only**:
- **Zero Child Participants:** No child participants, minors, learner records, student transcripts, or speech-pathology records enter the Stage 34 annotation system.
- **Prohibited Delivery:** No text evaluated in Stage 34 is approved for unsupervised or direct child delivery. `approved_for_child_delivery` remains strictly `false`.
- **Safeguarding Escalation:** If any text candidate contains distressing, dangerous, or unsafe content, reviewers trigger the `SAFETY_CONCERN` reason code, routing the item immediately to senior governance escalation.

---

## 4. Privacy, Security, and Storage Boundaries

### 4.1 External Protected Storage Isolation

In accordance with Governance Invariant 13 and Invariant 14, all restricted texts, reviewer personal identifying information (PII), consent signatures, compensation ledgers, and raw adjudication rationales reside strictly outside the Git repository:

```text
<SINHALA_EXPERT_VALIDATION_PROTECTED_ROOT>/stage34/
├── reviewers/        # Reviewer credentials, CVs, signed consents, qualification records
├── assignments/      # Secure tokens mapping reviewers to batches
├── item_text/        # Full text pairs (source and candidates)
├── annotations/      # Immutable original JSON submissions
├── amendments/       # Versioned amendment records
├── adjudications/    # Adjudication rationales and notes
├── comments/         # Free-text commentary
├── exports/          # Restricted audit exports
└── audit/            # Append-only security and operational audit logs
```

The protected root is verified during WP0 and WP1 startup to ensure it resides outside the working tree (`c:\Users\Lasindu\Documents\GitHub\Language_Simplification_MVP`). Any configuration pointing within the working tree results in immediate, fail-closed termination.

### 4.2 Repository-Safe Public Artifacts

Repository-tracked files contain only:
- Schemas, algorithms, test fixtures, and scripts;
- Pseudonymous reviewer identifiers (`REV-S34-XXX`);
- Opaque item identifiers (`ITEM-S34-XXXXXX`) and assignment identifiers (`ASN-S34-XXXXXX`);
- Controlled categorical labels and reason codes;
- Aggregated agreement statistics, confusion matrices, and Krippendorff's alpha point estimates/CIs;
- Cryptographic verification hashes.

---

## 5. Reviewer Conflict of Interest Policy

To ensure impartiality:
1. **Rule Authorship:** Authors of specific Stage 33 rules are disqualified from reviewing candidates generated by those rules.
2. **Adjudication Independence:** An adjudicator cannot adjudicate an item if they were a primary reviewer on that item.
3. **Project-Team Isolation:** Core development team annotations are separated from independent expert annotations and excluded from primary agreement calculations.
4. **Institutional Conflicts:** Reviewers with employment or financial conflicts regarding source publishers are excluded from affected evaluation strata.

---

## 6. Audit Logging and Traceability

Every administrative and review event is captured in an append-only JSONL log (`stage34_audit_log.jsonl`) tracking:
- Event ID (`EVT-XXXXXXXXXXXX`);
- UTC Timestamp (ISO 8601);
- Pseudonymous Actor ID;
- Lifecycle Action (`ASSIGNMENT_CREATED`, `ANNOTATION_SUBMITTED`, `AMENDMENT_RECORDED`, `ADJUDICATION_RESOLVED`);
- Object ID;
- Reason code and outcome disposition;
- Request UUID.

Audit logs never record raw candidate text, source text, reviewer legal names, or contact credentials.
