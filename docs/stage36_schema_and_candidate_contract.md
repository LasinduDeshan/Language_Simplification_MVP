# Stage 36 — Schema, Data Contracts, and Envelope Specifications

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Package:** `backend/app/sinhala_output_validation/schemas.py`  

---

## 1. Pydantic v2 Base Configuration

All data models inherit from `StrictBaseModel`:
```python
class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True
    )
```

---

## 2. Core Schemas

### 2.1 CandidateEnvelope
Represents the provider-neutral envelope carrying source and candidate texts, rights profiles, and execution receipts:
- `candidate_id`: Unique identifier (min length 5).
- `request_id`: Correlation request ID.
- `parent_candidate_id`: Parent candidate ID if generated via fallback.
- `fallback_depth`: Integer $\in [0, 3]$.
- `fallback_reason_code`: Reason code triggering the fallback attempt.
- `source_record_id`: Opaque source record ID.
- `source_text_ref`: Protected URI reference (`protected://sources/...`).
- `source_text_sha256_internal`: 64-char hex SHA-256.
- `candidate_text_ref`: Protected URI reference (`protected://candidates/...`).
- `candidate_text_sha256_internal`: 64-char hex SHA-256.
- `provider_condition`: `C0_RULE_BASELINE`, `C1_GEMINI_EXPERIMENTAL`, `C2_MT5_EXPERIMENTAL`, `C3_MBART_EXPERIMENTAL`.
- `execution_mode`: `REAL_PROVIDER`, `REAL_LOCAL_MODEL`, `CACHED_EMPIRICAL`, `SIMULATED`, `RULE_ENGINE`.
- `external_processing_authorized`: Boolean (strictly required `True` for `REAL_PROVIDER` Gemini).
- `generation_configuration_hash`: 16+ character configuration hash.

### 2.2 TextSpan
Defines exact Unicode code-point offsets $[start, end)$:
- `start`: Non-negative integer offset.
- `end`: Strictly greater than `start`.
- `text`: Slice text for audit verification.

### 2.3 ValidatorFinding
Granular gate violation or diagnostic finding emitted by validators V0–V8:
- `finding_id`: Unique identifier (min length 5).
- `validator_id`: Emitting validator ID (min length 3).
- `validator_version`: Validator semver string.
- `severity`: `CRITICAL`, `REVIEW`, `WARNING`, `DIAGNOSTIC`.
- `reason_code`: Standardized uppercase reason code.
- `evidence_class`: `AUTHORITATIVE_DETERMINISTIC`, `GOVERNED_HEURISTIC`, `AUTOMATED_PROXY`, `HUMAN_EXPERT_DECISION`.
- `span_category`: `DECLARED_PROTECTED_SPAN`, `DETERMINISTIC_PROTECTED_SPAN`, `INFERRED_PROTECTED_SPAN`.
- `source_spans`: List of `TextSpan`.
- `candidate_spans`: List of `TextSpan`.
- `public_summary`: Privacy-safe public summary string without raw texts.

### 2.4 ValidationResult
Comprehensive terminal result of candidate validation:
- `validation_result_id`: Unique result ID.
- `candidate_id`: Evaluated candidate ID.
- `configuration_hash`: Frozen configuration hash.
- `execution_outcome`: `COMPLETED` or `FAILED_INTERNAL`.
- `candidate_disposition`: Exactly one terminal disposition if `COMPLETED`; null if `FAILED_INTERNAL`.
- `automated_validation_status`: `NOT_STARTED`, `PARTIALLY_COMPLETED`, `COMPLETED`, `FAILED_INTERNAL`.
- `completed_validator_count`: Integer $\in [0, 9]$.
- `expected_validator_count`: Integer (default 9).
- `critical_gate_passed`: Boolean.
- `fallback_required`: Boolean.
- `findings`: List of `ValidatorFinding`.
- `approved_for_child_delivery`: Immutable safety invariant (`False`).
- `approved_for_unsupervised_child_delivery`: Immutable safety invariant (`False`).
- `requires_expert_review`: Immutable governance invariant (`True`).
