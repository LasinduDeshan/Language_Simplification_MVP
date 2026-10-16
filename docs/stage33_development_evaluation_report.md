# Stage 33 — Train-Only Development Evaluation Report

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Training partition evaluation, rule applicability, guard filtering, candidate ranking, and disposition outcomes  
**Evaluation Denominator:** 124 Training Records of Canonical Analytical Corpus View (`canonical_analytical_150`)  
**Status:** Evaluation Completed & Reconciled  

---

## 1. Executive Summary

Development evaluation was executed exclusively on the 124 training split records of the Stage 31 canonical analytical corpus view. All 8 frozen rules were evaluated deterministically without mutating input records.

### Core Metrics Summary

- **Submitted Training Inputs:** 124
- **Draft Rewrites Selected:** 54 (43.5%)
- **Unchanged Fallbacks (No Applicable Rule):** 70 (56.5%)
- **Unchanged Fallbacks (All Candidates Blocked):** 0 (0.0%)
- **Manual Review Required:** 0 (0.0%)
- **Failed Internal Errors:** 0 (0.0%)
- **Rule Evaluation Attempts:** 1,001
  - `CANDIDATE_GENERATED`: 74
  - `BLOCKED_MEANING_GUARD`: 5
  - `BLOCKED_PROTECTED_SPAN`: 0
  - `NOT_APPLICABLE`: 922
- **Candidates Generated:** 74
  - `SELECTED`: 54
  - `NOT_SELECTED_LOWER_RANK`: 20
  - `BLOCKED_MEANING_GUARD`: 0
  - `BLOCKED_PROTECTED_SPAN`: 0
- **Transformation Operations Recorded:** 74
- **Protected-Span Violations:** 0
- **Pipeline-Introduced `U+FFFD`:** 0
- **Unaccounted Units Across All Levels:** **0**

---

## 2. Rule-Level Application Metrics

| Rule ID | Rule Type | Priority | Matches / Attempts | Generated | Guard Blocked | Selected |
|---|---|---|---|---|---|---|
| `SI-PHR-SUB-0001` | PHRASE_SUBSTITUTION | 150 | 124 | 1 | 0 | 1 |
| `SI-PHR-SUB-0002` | PHRASE_SUBSTITUTION | 140 | 124 | 0 | 0 | 0 |
| `SI-LEX-SUB-0001` | LEXICAL_SUBSTITUTION | 100 | 124 | 15 | 0 | 14 |
| `SI-LEX-SUB-0002` | LEXICAL_SUBSTITUTION | 90 | 124 | 4 | 5 | 2 |
| `SI-LEX-SUB-0003` | LEXICAL_SUBSTITUTION | 80 | 124 | 2 | 0 | 0 |
| `SI-SYN-CON-0001` | CONSERVATIVE_SYNTACTIC | 70 | 124 | 2 | 0 | 2 |
| `SI-SNT-SPL-0002` | SENTENCE_SPLIT | 60 | 124 | 6 | 0 | 5 |
| `SI-SNT-SPL-0001` | SENTENCE_SPLIT | 50 | 124 | 44 | 0 | 30 |
| **Total** | | | **1,001** | **74** | **5** | **54** |

---

## 3. Two-Stage Candidate Resolution Analysis

During Stage 1 eligibility filtering, 5 rule attempts of `SI-LEX-SUB-0002` (`තවදුරටත්` → `තවත්`) were safely blocked because they appeared immediately preceding negation markers (`නැත`), preserving the idiom "no longer" without syntactic disruption.

In Stage 2 ranking, eligible candidates were ranked by frozen precedence (`LONGEST_APPROVED_PHRASE_MATCH` → `HIGHER_RULE_PRIORITY` → `FEWER_TRANSFORMATIONS` → `LOWER_EDIT_DISTANCE` → `STABLE_RULE_ID_ORDER`). Exactly 54 top candidates were selected, and 20 competing candidates were assigned `CandidateTerminalStatus.NOT_SELECTED_LOWER_RANK`.

---

## 4. Governance Status & Child Safety Disclaimer

Every selected rewrite in this report maintains:
- `validation_status: "draft"`
- `expert_validated: false`
- `approved_for_child_delivery: false`
- `requires_expert_review: true`

Automated gate passage establishes technical determinism and meaning preservation invariants. It does not certify linguistic naturalness or suitability for children.
