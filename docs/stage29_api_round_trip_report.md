# Stage 29 — Backend API & Serialization Round-Trip Report

**Component:** Component 3 — Language Simplification MVP  
**Stage:** Stage 29 (Sinhala Database, UI and Font Support)  
**Status:** PASSED  
**Execution Timestamp:** 2026-10-14T10:45:00Z  

---

## 1. Executive Summary

The backend API and serialization services were verified for exact Unicode code-point preservation, request tamper protection, and byte-level export fidelity:
- `LocaleSelectionRequest` (`extra="forbid"`) strictly enforces server-side derivation of script and direction. Any client attempt to inject extra metadata returns HTTP 422.
- The field-specific invisible-character policy enforces the versioned denylist (`control_character_policy.json`). Legitimate ZWJ/ZWNJ characters in allowlisted fixture sequences are preserved; denylisted controls in identifiers or usernames are rejected.
- Decoded Unicode equality is verified across API request and response boundaries.
- JSON and CSV exports were verified for byte-level integrity, UTF-8 encoding, and SHA-256 reproducibility.

---

## 2. API Endpoint Verification Summary

| Endpoint | Method | Test Verification | Status |
|---|---|---|---|
| `/api/v1/localization/locales` | GET | Returns canonical `si-LK`, `en-LK`, and default fallback | **PASSED** |
| `/api/v1/localization/locale` | POST | Accepts `LocaleSelectionRequest`, derives script & direction | **PASSED** |
| `/api/v1/localization/locale` | POST | Rejects extra client metadata fields (`script`, `direction`) with 422 | **PASSED** |
| `/api/v1/localization/probe/round-trip` | POST | Exact code-point equality across JSON payload | **PASSED** |
| `/api/v1/localization/content` | POST | Persists localized content with field control validation | **PASSED** |
| `/api/v1/localization/content/{id}` | GET | Retrieves localized content with intact Unicode | **PASSED** |
| `/api/v1/localization/export/json` | GET | Returns UTF-8 JSON with `X-Artifact-SHA256` header | **PASSED** |
| `/api/v1/localization/export/csv` | GET | Returns UTF-8 CSV with optional BOM and SHA-256 header | **PASSED** |

---

## 3. Grapheme Cluster Limits & Counting

Extended grapheme clusters according to Unicode UAX #29 were validated:
- Visual characters containing consonant + virama + ZWJ + consonant (e.g. Bandi akuru `ක්‍ෂ`, 4 code units) evaluate to exactly **1 grapheme cluster**.
- Multi-syllable Sinhala words (e.g. `අම්මා`, 5 code units) evaluate to exactly **3 grapheme clusters**.
- Maximum-length validation relies on grapheme cluster counting rather than UTF-16 code units (`string.length`).

---

## 4. Privacy and Security Guardrails

- Logs escape all invisible and directional control codes (`\u200d`, `\u202e`) via `escape_controls_for_log`.
- No raw learner text or authentication credentials are exposed in API logs or fixtures.
- All technical records default to `approved_for_child_delivery: false`.
