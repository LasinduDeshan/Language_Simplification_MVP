# Stage 32 Lexicon Governance and Schema Specification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Deliverable:** Governance and Data Contract Specification  
**Stage:** Stage 32 — Sinhala Child-Vocabulary Lexicon Construction  
**Status:** Authoritative — Governed Schema Freeze  

---

## 1. Executive Summary & Governance Purpose

Stage 32 establishes a strictly governed, reproducible, and privacy-preserving data contract architecture for extracting candidate child-vocabulary items in Sinhala (`si`, `si-LK`, script `Sinh`) from the authoritative Stage 31 pilot corpus. 

The schemas defined herein enforce:
1. **Multi-Tier Linguistic Decoupling:** Separation between observed token occurrences, surface variants, candidate canonical forms, automated morphological hypotheses, and semantic meanings.
2. **Independent Occurrence and Entry Accounting:** Separate terminal disposition state machines for occurrence-level accounting and candidate entry-level accounting.
3. **Exact Code-Point Offsets:** Strict enforcement of zero-based, half-open intervals `[normalized_start_code_point, normalized_end_code_point)`.
4. **Field-Level Rights Governance:** Granular rights resolution distinguishing standalone lexical forms from restricted concordance passages and sentences.
5. **Privacy & Content Protection:** Protected storage abstraction (`protected://...`) and runtime keyed HMAC generation with domain separation.
6. **No Automated Child Approval:** Automatic defaults ensuring `approved_for_child_delivery: false`, `expert_validated: false`, and `validation_status: "draft"`.

---

## 2. Separate Occurrence & Entry Disposition State Machines

To prevent accounting ambiguity, Stage 32 defines two distinct, non-overlapping disposition contracts.

### 2.1 Occurrence Disposition (`OccurrenceDisposition`)

Every token occurrence encountered in the 150 canonical analytical records receives exactly one occurrence disposition evaluated from left to right:

```text
REJECTED_PRIVACY_OR_SECURITY
→ REJECTED_INVALID_SOURCE_EVIDENCE
→ EXCLUDED_TOKEN_CLASS
→ MANUAL_REVIEW_OCCURRENCE
→ INCLUDED_CANDIDATE_OCCURRENCE
```

| Occurrence Disposition | Description |
|---|---|
| `REJECTED_PRIVACY_OR_SECURITY` | Token contains sensitive, private, or credentials-bearing data. |
| `REJECTED_INVALID_SOURCE_EVIDENCE` | Token associated with corrupted, unverifiable, or invalid source metadata. |
| `EXCLUDED_TOKEN_CLASS` | Punctuation, standalone numbers, symbols, URLs, or non-lexical tokens. |
| `MANUAL_REVIEW_OCCURRENCE` | Mixed-script, unexpected joiners, suspected OCR artifact, or sensitive terms. |
| `INCLUDED_CANDIDATE_OCCURRENCE` | Governed Sinhala word token eligible for candidate extraction. |

### 2.2 Terminal Entry Disposition (`TerminalEntryDisposition`)

Every extracted candidate entry receives exactly one terminal entry disposition using first-matching precedence:

```text
REJECTED_PRIVACY_OR_SECURITY
→ REJECTED_INVALID_SOURCE_EVIDENCE
→ EXCLUDED_NON_LEXICAL
→ EXCLUDED_NON_SINHALA
→ MANUAL_REVIEW_REQUIRED
→ ACCEPTED_DRAFT_LEXICON_ENTRY
```

| Terminal Entry Disposition | Description |
|---|---|
| `REJECTED_PRIVACY_OR_SECURITY` | Entry violates privacy, PII, or security policies. |
| `REJECTED_INVALID_SOURCE_EVIDENCE` | Entry lacks reproducible provenance across all contributing sources. |
| `EXCLUDED_NON_LEXICAL` | Non-lexical symbols, boilerplate, or malformed OCR artifacts. |
| `EXCLUDED_NON_SINHALA` | Pure Latin, foreign script, or non-Sinhala vocabulary. |
| `MANUAL_REVIEW_REQUIRED` | Ambiguous morphology, multi-rule ties, or low automated confidence. |
| `ACCEPTED_DRAFT_LEXICON_ENTRY` | Accepted into draft candidate lexicon for expert review. |

---

## 3. Core Pydantic v2 Schemas

### 3.1 Candidate Lexicon Entry (`CandidateLexiconEntry`)

The primary unit of analysis in the draft lexicon:

```python
class CandidateLexiconEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    language: str = "si"
    locale: str = "si-LK"
    script: str = "Sinh"
    canonical_form: str
    candidate_lemma: Optional[str] = None
    lemma_method: LemmaMethod = LemmaMethod.IDENTITY_CANONICAL
    lemma_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    surface_forms: List[SurfaceFormRecord] = Field(default_factory=list)
    token_class: str = "SINHALA_WORD"
    grapheme_count: int = Field(..., ge=0)
    code_point_count: int = Field(..., ge=0)
    syllable_proxy_count: Optional[int] = Field(default=None, ge=0)
    morphology_hypotheses: List[MorphologyHypothesis] = Field(default_factory=list)
    canonical_frequency: int = Field(..., ge=0)
    canonical_document_frequency: int = Field(..., ge=0)
    weighted_provenance_frequency: float = Field(..., ge=0.0)
    source_count: int = Field(..., ge=0)
    source_frequency_distribution: Dict[str, int] = Field(default_factory=dict)
    eligible_source_count: int = Field(..., ge=1)
    observed_source_count: int = Field(..., ge=0)
    source_dispersion: float = Field(..., ge=0.0, le=1.0)
    dispersion_formula_version: str = "fixed_k_entropy_v1"
    provisional_band: ProvisionalVocabularyBand = ProvisionalVocabularyBand.REVIEW_REQUIRED
    band_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    band_evidence: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)
    rights_profile_refs: List[RightsProfileReference] = Field(default_factory=list)
    field_export_policies: Dict[str, FieldExportPolicy] = Field(default_factory=dict)
    terminal_entry_disposition: TerminalEntryDisposition = TerminalEntryDisposition.ACCEPTED_DRAFT_LEXICON_ENTRY
    validation_status: str = "draft"
    expert_validated: bool = False
    research_eligible: bool = False
    approved_for_child_delivery: bool = False
    approved_for_unsupervised_child_delivery: bool = False
    requires_expert_review: bool = True
```

### 3.2 Token Occurrence Record (`TokenOccurrenceRecord`)

Losslessly accounts for each individual token occurrence:

```python
class TokenOccurrenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    occurrence_id: str = Field(..., pattern=r"^SI-OCC-\d{8}$")
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    canonical_record_id: str
    provenance_record_id: str
    source_id: str
    split_group_id: str
    token_index: int = Field(..., ge=0)
    normalized_start_code_point: int = Field(..., ge=0)
    normalized_end_code_point: int = Field(..., ge=0)
    offset_interval: str = "zero_based_half_open"
    surface_form_hmac: Optional[str] = None
    hmac_key_id: str = "HMAC-2026-V1"
    hmac_scheme_version: str = "v1"
    hmac_domain: str = "sinhala-lexicon-surface-form"
    context_storage_ref: str
    token_text_storage_ref: str
    exact_duplicate_weight: float = Field(default=1.0, gt=0.0)
    rights_profile_id: str
    rights_profile_version: int = Field(default=1, ge=1)
    stage30_configuration_hash: str
    stage31_configuration_hash: str
    corpus_artifact_sha256: str
    occurrence_disposition: OccurrenceDisposition
    exclusion_reason_code: Optional[str] = None
```

### 3.3 Morphology Hypothesis (`MorphologyHypothesis`)

Captures automated inflectional and derivational groupings:

```python
class MorphologyHypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rule_id: str
    rule_version: str = "1.0.0"
    base_form: str
    inflected_form: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    linguistic_note: Optional[str] = "Illustrative rule-based morphology hypothesis; not expert-validated linguistic evidence."
```

*Linguistic Disclaimer:* All automated morphology hypotheses are tentative technical groupings. They do not constitute human linguistic validation.

### 3.4 Expert Review Record (`LexiconExpertReviewRecord`)

Governed data structure for future human expert assessment:

```python
class LexiconExpertReviewRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry_id: str = Field(..., pattern=r"^SI-LEX-\d{6}$")
    reviewer_id: Optional[str] = None
    reviewer_role: str = "sinhala_linguist_or_early_childhood_language_expert"
    independent_review_round: int = Field(default=1, ge=1)
    lemma_decision: ReviewDecision = ReviewDecision.NOT_REVIEWED
    age_band_decision: AgeBandReviewDecision = AgeBandReviewDecision.NOT_REVIEWED
    meaning_review_status: ReviewDecision = ReviewDecision.NOT_REVIEWED
    safety_status: ReviewDecision = ReviewDecision.NOT_REVIEWED
    comments_storage_ref: Optional[str] = None
    reviewed_at: Optional[str] = None
```

*Model Integrity Validator:* `reviewed_at` cannot be populated if `reviewer_id` is null or if all review decisions remain `NOT_REVIEWED`.

---

## 4. Rights Inheritance & Field-Level Export Matrix

Every lexicon entry records version-pinned rights profiles inherited from all contributing sources:

```json
"rights_profile_refs": [
  {
    "source_id": "SRC-SI-001",
    "rights_profile_id": "RP-SRC-SI-001",
    "rights_profile_version": 1
  }
]
```

### Field-Level Exposure Policies

| Field | Permitted Export Policy | Public Exposure Safety Rule |
|---|---|---|
| `canonical_form` | `PUBLIC_PERMITTED_STANDALONE` | Allowed standalone without context if source permits derived processing. |
| `frequencies` ($f_c, df_c, f_w$) | `PUBLIC_PERMITTED_AGGREGATE` | Numerical aggregations are public. |
| `source_dispersion` ($D_s$) | `PUBLIC_PERMITTED_AGGREGATE` | Normalized entropy metric is public. |
| `surface_forms` | `PUBLIC_PERMITTED_STANDALONE` | Standalone isolated words only; no sequences. |
| `context_storage_ref` | `RESTRICTED_PROTECTED_INTERNAL` | Never public; stored under `protected://`. |
| `definitions` / `meanings` | `RESTRICTED_PROTECTED_INTERNAL` | Protected until independent rights clearance. |

---

## 5. Security & Privacy Controls

1. **Physical Storage Decoupling:** Raw text and concordances reside strictly outside Git under `SINHALA_LEXICON_PROTECTED_ROOT`.
2. **Keyed HMAC Domain Separation:** Public occurrence identifiers use keyed HMAC digests with domain separation:
   $$\text{HMAC}(\text{key}, \text{"sinhala-lexicon-surface-form:v1:"} \parallel \text{occurrence\_id} \parallel \text{surface\_form})$$
   `surface_form_hmac` is set to `null` in schemas and populated exclusively during runtime execution using the protected server-side key.
3. **Zero Plaintext Hashes:** Unkeyed SHA-256 digests of short words or contexts are strictly banned from Git commits.
