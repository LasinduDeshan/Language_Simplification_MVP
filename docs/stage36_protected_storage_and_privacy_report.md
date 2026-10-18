# Stage 36 — Protected Storage and Privacy Routing Architecture

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Modules:** `backend/app/sinhala_output_validation/storage.py`  

---

## 1. Storage Isolation Boundary

- **Filesystem Confinement:** Raw candidate outputs, source texts, and evaluation payloads are stored in an access-controlled filesystem root determined by `SINHALA_OUTPUT_VALIDATION_PROTECTED_ROOT`, strictly residing outside the git repository.
- **Path Traversal Defense:** Canonical path resolution enforces strict containment within the root, forbidding `..` traversal and symlink breakouts.
- **Atomic File Operations:**
  - File writes utilize `tempfile.NamedTemporaryFile` in target subdirectories.
  - Flushed and synced via `os.fsync`.
  - Atomically swapped into position using `os.replace`.
  - Immediate post-write SHA-256 verification against calculated in-memory hash.

---

## 2. Hash-Chained Cryptographic Audit Layer

- **Append-Only Merkle-Chain:**
  - Each audit event record binds to the HMAC signature of the preceding entry via `prev_hmac_sha256`.
  - Genesis block initializes `prev_hmac_sha256 = "0" * 64`.
  - 256-bit keyed HMAC signature (`HMAC-SHA256`) signs `{"seq", "prev_hmac_sha256", "event_type", "payload"}` using `stage36-public-provenance-v1`.
  - Any insertion, deletion, or modification of a prior log line invalidates all subsequent signatures in the chain.

---

## 3. Public vs. Protected Metadata Boundary

- **Public Telemetry:** `PublicDiagnosticLogger` emits only sanitized event metadata (candidate ID, validator ID, reason code, severity, diagnostic metrics) with zero raw texts or PII.
- **Protected Telemetry:** Unsanitized evaluation records remain strictly in the protected root and are referenced in public records via opaque URI schemes (`protected://sources/...`, `protected://candidates/...`).
