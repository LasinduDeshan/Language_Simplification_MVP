# Stage 31 — Quality and Exclusion Report

**Stage:** Stage 31 — Sinhala External Dataset Ingestion and Pilot Corpus Creation  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** `docs/stage31_quality_and_exclusion_report.md`  
**Status:** Frozen — Privacy and Quality Screening Sealed  
**Authoritative Prerequisite:** `stage-30-complete-v3` (`ef95667b53dddfb032e71fc51d6c524aff7a22a2`)

---

## 1. Executive Summary

In Work Package 6 (WP6), all 180 preprocessed records were screened for privacy vulnerabilities, credentials, formatting corruption, and length anomalies.

- **Privacy and Security Screening:** Regular expression scanning for emails, Sri Lankan telephone numbers, NIC identifiers, and private API keys.
- **Quality Thresholds:** Evaluated against minimum length (3 tokens), maximum length (400 tokens), and consecutive word repetition.
- **Terminal Disposition Order:** Strictly applied first-matching precedence order from Section 14.3.
- **Quarantine Isolation:** Any flagged private or insecure content is stored strictly in external protected quarantine storage and omitted from repository records.

---

## 2. Terminal Disposition Accounting

In accordance with Section 18.4 of the Implementation Plan:

$$
\text{CandidateRecords (180)} = \text{Accepted (180)} + \text{ManualReview (0)} + \text{Rejected (0)} + \text{Excluded (0)} + \text{Quarantined (0)} + \text{Unaccounted (0)}
$$

$$\text{Accounting Status: 0 Unaccounted (RECONCILED)}$$

| Terminal Disposition | Count | Accounting Category | Disposition Description |
|---|---|---|---|
| **`ACCEPTED_PILOT_CANDIDATE`** | **180** | Accepted | Passed all privacy, quality, and rights gates |
| `REJECTED_RIGHTS` | 0 | Rejected | Unapproved rights or expired profile |
| `REJECTED_SECURITY` | 0 | Rejected | Private tokens, API keys, or credentials |
| `REJECTED_PRIVACY` | 0 | Rejected | PII (email, phone, national ID) |
| `REJECTED_INVALID_UNICODE` | 0 | Rejected | Prohibited controls or replacement marks |
| `MANUAL_REVIEW_REQUIRED` | 0 | ManualReview | Questionable orthographic or script context |
| `EXCLUDED_NON_SINHALA` | 0 | Excluded | Insufficient Sinhala script ratio |
| `REJECTED_QUALITY` | 0 | Rejected | Extreme length or excessive repetition |
| **Unaccounted** | **0** | Reconciled | Zero lost or unclassified records |

---

## 3. Development Pool Calibration Evidence

The 90 predeclared method-development units (`is_method_development_record: true`) were analyzed to calibrate quality filters:
- Sentence lengths in educational narratives (StoryWeaver) ranged between 10 and 45 tokens.
- Encyclopedic paragraphs (Wikipedia) averaged 60 to 90 tokens.
- No natural early-grade sentences were rejected by the minimum 3-token threshold.
- No false-positive PII flags were triggered on standard Sinhala historical dates or numerals.

---

## 4. Verification Signoff

```text
Total Evaluated Records:       180
Accepted Pilot Candidates:      180 (Minimum viable required: 150)
Zero-Loss Accounting:          PASSED (0 unaccounted)
Quarantined Records:           0
PII / Secret Leakage in Git:   0
Timestamp:                     2026-10-15T16:26:00Z
Verifier:                      REV-GOV-01
```

