# Stage 36 — Unicode, Language, and Structure Validation Gates

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Modules:** `backend/app/sinhala_output_validation/validators/v0_v2_structural.py`  

---

## 1. Validator V0: Envelope & Provenance Gate

- **Purpose:** Verifies envelope integrity, cryptographic configuration hash matching, and execution mode compatibility.
- **Rules:**
  - If `execution_mode == REAL_PROVIDER` and `provider_condition == C1_GEMINI_EXPERIMENTAL`, `external_processing_authorized` must be `True`.
  - `generation_configuration_hash` must match the frozen bundle hash (`stage36_configuration.json`).
- **Severity on Failure:** `CRITICAL`
- **Reason Code:** `REJ_CONF_PROVENANCE_INVALID`

---

## 2. Validator V1: Unicode Serialization, NFC Compatibility and Script-Validation Gate

- **Purpose:** Verifies that candidate output is NFC-compatible and strictly adheres to the Sinhala script specification without silently modifying or rewriting candidate output. Original candidate bytes are immutably preserved.
- **Rules:**
  - **NFC Compatibility:** Verifies `unicodedata.normalize('NFC', candidate_text) == candidate_text`. Rejects decomposed or malformed combining sequences.
  - **Control Character Prohibition:** Forbids all non-printable control characters (`\x00-\x08`, `\x0B-\x0C`, `\x0E-\x1F`, `\x7F-\x9F`), allowing only standard whitespace (`\n`, `\t`, `\r`, space).
  - **Mojibake Detection:** Rejects Unicode replacement characters (`\uFFFD`) and broken encodings.
  - **Script Ratio:** Sinhala Unicode block characters (`U+0D80`–`U+0DFF`) must comprise at least 50% of all alphabetic characters in the candidate output.
- **Severity on Failure:** `CRITICAL`
- **Reason Code:** `REJ_INVALID_UNICODE`

---

## 3. Validator V2: Structure and Length Bounds Gate

- **Purpose:** Enforces non-empty output and bounds expansion/compression ratios relative to source text.
- **Rules:**
  - **Non-Empty:** Rejects empty or whitespace-only candidates.
  - **Length Ratio Bounds:** Character length ratio $\frac{\text{len(candidate)}}{\text{len(source)}}$ must lie within $[0.20, 3.00]$.
    - Ratio $< 0.20$ indicates severe proposition truncation.
    - Ratio $> 3.00$ indicates hallucinatory length explosion.
  - **No-Op Diagnostic:** Identifies candidates identical to source text and tags them with diagnostic reason code `DIAG_UNCHANGED_SOURCE`.
- **Severity on Failure:** `CRITICAL`
- **Reason Code:** `REJ_CRITICAL_SEMANTIC_RISK`
