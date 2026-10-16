# Stage 33 — Schema and Trace Contract Specification

**Project:** AI-Powered Adaptive Child-Friendly Language Simplification System  
**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Data contracts, request provenance bindings, qualified transformation tracing, and public/protected separation  
**Governance Checkpoint:** Stage 33 Technical Draft  

---

## 1. Request Provenance Contract

Every rewrite request cryptographically binds upstream configuration hashes, split manifests, and rights profile versions:

```json
{
  "request_id": "SI-SIMP-REQ-000001",
  "record_id": "SI-PILOT-000001",
  "source_storage_ref": "protected://sinhala_external/inputs/SI-PILOT-000001.txt",
  "source_sha256_internal": "64_char_hex",
  "language": "si",
  "stage30_configuration_hash": "64_char_hex",
  "stage31_split_manifest_hash": "64_char_hex",
  "stage31_corpus_view": "canonical_analytical_150",
  "stage32_configuration_hash": "64_char_hex",
  "stage32_lexicon_manifest_hash": "64_char_hex",
  "stage33_configuration_hash": "64_char_hex",
  "rights_profile_ids_and_versions": [
    {"rights_profile_id": "SRC-SI-001-RP-01", "version": 1}
  ],
  "partition": "train"
}
```

---

## 2. Mutually Exclusive Terminal Status Contracts

To maintain exact conservation equations without overlapping categories, rule attempts and candidates report mutually exclusive terminal statuses.

### 2.1 RuleAttemptTerminalStatus
- `NOT_APPLICABLE`: Pattern was not present in the input text.
- `BLOCKED_PROTECTED_SPAN`: Matched pattern overlaps with a protected meaning element.
- `BLOCKED_MEANING_GUARD`: Matched pattern violates negation, modality, or structure.
- `CANDIDATE_GENERATED`: Successfully generated a draft rewrite candidate.
- `DEFERRED_MANUAL_REVIEW`: Ambiguous context (e.g., subject recovery) routed to manual review.
- `FAILED_INTERNAL`: Unhandled exception or internal pipeline failure.

### 2.2 CandidateTerminalStatus
- `SELECTED`: Selected as the draft rewrite for output generation.
- `NOT_SELECTED_LOWER_RANK`: Eligible candidate passed all guards but was ranked below another candidate.
- `BLOCKED_PROTECTED_SPAN`: Candidate text mutates or drops a protected span.
- `BLOCKED_MEANING_GUARD`: Candidate violates negation, number, modality, quotation, or Unicode invariants.
- `DEFERRED_MANUAL_REVIEW`: Candidate requires human adjudication.
- `FAILED_INTERNAL`: Internal failure during evaluation.

---

## 3. Qualified Transformation Traceability

Stage 33 does not assert that all transformations map one-to-one. Traces record explicit mapping cardinality and exactness flags:

| Mapping Status | Cardinality / Nature | `mapping_exact` |
|---|---|---|
| `one_to_one` | Single source span to single output span | `true` |
| `many_to_one` | Multiple source spans to single output span | `true` |
| `one_to_many` | Single source span expanded to multiple output spans | `true` |
| `inserted` | Output span created without source counterpart | `false` |
| `deleted` | Source span removed without output counterpart | `false` |
| `reordered` | Source span transposed to different position | `false` |
| `non_local` | Sentence split or long-distance structural shift | `false` |
| `unmapped` | Fallback state for untraced boundary edits | `false` |

---

## 4. Public vs Protected Separation

1. **Restricted Text Quarantine:**
   - Raw source text, candidate rewrite text, and final output text reside strictly in external storage (`SINHALA_SIMPLIFICATION_PROTECTED_ROOT`).
   - If this root resolves within the repository worktree, the pipeline immediately fails closed.
2. **Public Metadata Sanitization:**
   - Public ledgers contain opaque IDs, rule IDs, terminal statuses, counts, and domain-separated keyed HMACs (`compute_keyed_hmac`).
   - Public ledgers contain zero reconstructable Sinhala text.
