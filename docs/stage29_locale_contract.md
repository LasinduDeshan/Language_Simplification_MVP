# Stage 29 — Language, Locale, and Security Contract

**Component:** Component 3 — Language Simplification MVP  
**Stage:** Stage 29 (Sinhala Database, UI and Font Support)  
**Contract Version:** `1.0.0`  
**Governed Default Locale:** `en-LK`  

---

## 1. Supported Language and Locales

| Purpose | Canonical Value | Aliases | Script | Direction | Status |
|---|---|---|---|---|---|
| Primary Sinhala Locale | `si-LK` | `si` | `Sinh` | `ltr` | Active |
| Default English Locale | `en-LK` | `en` | `Latn` | `ltr` | Active |

All language codes adhere to ISO 639-1 (`si`, `en`), script codes adhere to ISO 15924 (`Sinh`, `Latn`), and writing direction is `ltr` (left-to-right). Non-canonical names (e.g. `SIN`, `sinhala`, `lk-si`) are strictly rejected.

---

## 2. Server-Derived Metadata & Tamper Protection

Clients submit only the desired locale code via `LocaleSelectionRequest` (`model_config = ConfigDict(extra="forbid")`).
Script, direction, and canonical language are derived server-side from the trusted locale registry:

```json
{
  "language": "si",
  "locale": "si-LK",
  "script": "Sinh",
  "direction": "ltr",
  "content_status": "draft"
}
```

Any attempt by a client to submit custom `script`, `direction`, or mismatched metadata fields is strictly rejected with HTTP status **422 Unprocessable Entity**.

---

## 3. Versioned Control Character Policy

Policy definition: `data/sinhala_foundation/registry/control_character_policy.json` (Version `1.0.0`).

### Denylisted Characters

The following characters are strictly forbidden in identifiers, usernames, language codes, and file names:
- `U+200B` (Zero Width Space)
- `U+200C` (Zero Width Non-Joiner)
- `U+200D` (Zero Width Joiner)
- `U+200E` (Left-to-Right Mark)
- `U+200F` (Right-to-Left Mark)
- `U+202A` (Left-to-Right Embedding)
- `U+202B` (Right-to-Left Embedding)
- `U+202C` (Pop Directional Formatting)
- `U+202D` (Left-to-Right Override)
- `U+202E` (Right-to-Left Override)
- `U+2066` (Left-to-Right Isolate)
- `U+2067` (Right-to-Left Isolate)
- `U+2068` (First Strong Isolate)
- `U+2069` (Pop Directional Isolate)

### Field-Specific Rules

1. **Identifiers, Enums, Usernames, File Names:** Strictly reject any denylisted character.
2. **Educational Content:** Allow legitimate Zero-Width Joiner (`U+200D`) and Non-Joiner (`U+200C`) in allowlisted fixture sequences while flagging them for Stage 30 linguistic review. Reject unexpected directional overrides or non-printable controls.
3. **Logs:** Escape all control and invisible characters as `\uXXXX` sequences to prevent log injection.
4. **Technical Fixtures:** Preserve exact sequences for technical round-trip verification.

---

## 4. Frontend Storage Policy

1. Persist **only** the locale identifier string (`si-LK` or `en-LK`) under key `app_locale_preference` in `localStorage`.
2. **Never** write learner IDs, performance records, or screening scores to `localStorage`.
3. If the stored value is missing, unrecognized, or corrupted, fall back safely to `en-LK`.
