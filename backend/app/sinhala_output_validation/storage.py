"""
Protected storage, atomic file operations, path traversal defense, and cryptographic audit layer for Stage 36.
Ensures evaluation payloads and raw candidate texts are isolated outside the repository with integrity verification.
"""

import hashlib
import hmac
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional, Tuple

# Default local provenance key for deterministic audit HMAC signatures
DEFAULT_PROVENANCE_KEY = b"stage36-public-provenance-v1"
ENV_PROTECTED_ROOT = "SINHALA_OUTPUT_VALIDATION_PROTECTED_ROOT"
ENV_PROVENANCE_KEY = "SINHALA_OUTPUT_VALIDATION_PROVENANCE_KEY"


def get_protected_storage_root() -> Path:
    """
    Resolve the protected storage root directory.
    Defaults to an isolated directory in the system temp/user cache outside the git repository.
    """
    env_root = os.environ.get(ENV_PROTECTED_ROOT)
    if env_root:
        root_path = Path(env_root).resolve()
    else:
        # Default to a dedicated directory in user cache or tempdir outside repo
        base_temp = Path(tempfile.gettempdir()).resolve()
        root_path = (base_temp / "sinhala_output_validation_protected_storage").resolve()

    root_path.mkdir(parents=True, exist_ok=True)
    return root_path


def _resolve_safe_path(category: str, filename: str) -> Path:
    """
    Safely resolve target path under the protected storage root.
    Prevents path traversal, directory breakouts, and symlink hijacking.
    """
    root = get_protected_storage_root()

    # Reject dangerous characters
    if ".." in category or ".." in filename:
        raise ValueError(f"Path traversal detected in category='{category}' or filename='{filename}'")
    if "/" in filename or "\\" in filename:
        raise ValueError(f"Filename '{filename}' cannot contain path separators")

    target_dir = (root / category).resolve()

    # Ensure target_dir is strictly within root
    if not str(target_dir).startswith(str(root)):
        raise ValueError(f"Category '{category}' escapes protected root")

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = (target_dir / filename).resolve()

    if not str(target_path).startswith(str(root)):
        raise ValueError(f"Target path '{target_path}' escapes protected root")

    return target_path


def write_protected_content(
    category: str,
    filename: str,
    content: bytes,
    expected_sha256: Optional[str] = None
) -> Tuple[str, str]:
    """
    Atomically write content to the protected storage root.
    Uses tempfile + flush + fsync + os.replace to guarantee atomic persistence.
    Verifies post-write SHA-256 integrity against expected_sha256 if provided.
    Returns:
        (uri_ref, actual_sha256_hex)
    """
    target_path = _resolve_safe_path(category, filename)
    target_dir = target_path.parent

    # Compute expected hash
    calculated_sha256 = hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and calculated_sha256.lower() != expected_sha256.lower():
        raise ValueError(
            f"Pre-write integrity failure: expected SHA-256 {expected_sha256}, got {calculated_sha256}"
        )

    # Atomic write pattern
    temp_file = tempfile.NamedTemporaryFile(
        dir=target_dir,
        delete=False,
        prefix=".tmp_write_",
        suffix=".tmp"
    )
    temp_path = Path(temp_file.name).resolve()

    try:
        with temp_file:
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Atomic replacement
        os.replace(temp_path, target_path)

        # Post-write on-disk verification
        with open(target_path, "rb") as f:
            disk_content = f.read()
        disk_sha256 = hashlib.sha256(disk_content).hexdigest()

        if disk_sha256 != calculated_sha256:
            # Emergency removal of corrupted file
            if target_path.exists():
                target_path.unlink()
            raise IOError(
                f"Post-write integrity verification failed: disk SHA-256 {disk_sha256} != {calculated_sha256}"
            )

    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise

    uri_ref = f"protected://{category}/{filename}"
    return uri_ref, calculated_sha256


def read_protected_content(uri_ref: str) -> bytes:
    """
    Read protected content given a 'protected://category/filename' reference.
    Enforces path confinement within root.
    """
    prefix = "protected://"
    if not uri_ref.startswith(prefix):
        raise ValueError(f"Invalid protected URI '{uri_ref}'; must start with '{prefix}'")

    relative_part = uri_ref[len(prefix):]
    parts = relative_part.split("/")
    if len(parts) != 2:
        raise ValueError(f"Protected URI must be of the form 'protected://category/filename', got '{uri_ref}'")

    category, filename = parts[0], parts[1]
    target_path = _resolve_safe_path(category, filename)

    if not target_path.exists():
        raise FileNotFoundError(f"Protected content not found at '{uri_ref}' ({target_path})")

    with open(target_path, "rb") as f:
        return f.read()


class CryptographicAuditLogger:
    """
    Append-only audit logger generating hash-chained HMAC-SHA256 signatures for tamper detection.
    Each record binds to the cryptographic hash of the preceding record (prev_hmac_sha256).
    """

    GENESIS_PREV_HMAC = "0" * 64

    def __init__(self, log_filename: str = "stage36_audit_log.jsonl", key: Optional[bytes] = None):
        self.log_filename = log_filename
        self.key = key or os.environ.get(ENV_PROVENANCE_KEY, "").encode("utf-8") or DEFAULT_PROVENANCE_KEY
        self.log_path = _resolve_safe_path("audit_logs", self.log_filename)
        self.sequence_number, self.last_hmac = self._read_tail_state()

    def _read_tail_state(self) -> Tuple[int, str]:
        if not self.log_path.exists():
            return 0, self.GENESIS_PREV_HMAC
        count = 0
        last_sig = self.GENESIS_PREV_HMAC
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        count = rec.get("seq", count + 1)
                        last_sig = rec.get("hmac_sha256", last_sig)
                    except json.JSONDecodeError:
                        pass
        return count, last_sig

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record an audit event, bind to preceding record's HMAC, sign, and append.
        """
        self.sequence_number += 1
        record_to_sign = {
            "seq": self.sequence_number,
            "prev_hmac_sha256": self.last_hmac,
            "event_type": event_type,
            "payload": payload,
        }
        serialized = json.dumps(record_to_sign, sort_keys=True, ensure_ascii=False)
        signature = hmac.new(self.key, serialized.encode("utf-8"), hashlib.sha256).hexdigest()

        final_record = {
            **record_to_sign,
            "hmac_sha256": signature
        }

        self.last_hmac = signature
        line = json.dumps(final_record, ensure_ascii=False) + "\n"

        # Append write with fsync
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        return final_record

    def verify_log_integrity(self) -> Tuple[bool, int, Optional[str]]:
        """
        Verify all log records in sequence and their cryptographic hash-chaining.
        Returns:
            (is_valid, record_count, error_message)
        """
        if not self.log_path.exists():
            return True, 0, None

        expected_seq = 1
        expected_prev_hmac = self.GENESIS_PREV_HMAC

        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    return False, line_idx - 1, f"JSON parse error at line {line_idx}: {e}"

                if "hmac_sha256" not in record or "seq" not in record or "prev_hmac_sha256" not in record:
                    return False, line_idx - 1, f"Missing required fields at line {line_idx}"

                if record["seq"] != expected_seq:
                    return False, line_idx - 1, f"Sequence gap at line {line_idx}: expected {expected_seq}, got {record['seq']}"

                if record["prev_hmac_sha256"] != expected_prev_hmac:
                    return False, line_idx - 1, f"Hash-chain break at sequence {expected_seq}: expected prev {expected_prev_hmac}, got {record['prev_hmac_sha256']}"

                sig = record["hmac_sha256"]
                to_verify = {
                    "seq": record["seq"],
                    "prev_hmac_sha256": record["prev_hmac_sha256"],
                    "event_type": record["event_type"],
                    "payload": record["payload"],
                }
                serialized = json.dumps(to_verify, sort_keys=True, ensure_ascii=False)
                expected_sig = hmac.new(self.key, serialized.encode("utf-8"), hashlib.sha256).hexdigest()

                if sig != expected_sig:
                    return False, line_idx - 1, f"HMAC signature mismatch at sequence {expected_seq}"

                expected_prev_hmac = sig
                expected_seq += 1

        return True, expected_seq - 1, None


class PublicDiagnosticLogger:
    """
    Sanitized logger that emits only privacy-safe diagnostic telemetry.
    Never logs raw source text, candidate text, or PII.
    """

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def record_diagnostic(
        self,
        request_id: str,
        candidate_id: str,
        validator_id: str,
        reason_code: str,
        severity: str,
        public_summary: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event = {
            "request_id": request_id,
            "candidate_id": candidate_id,
            "validator_id": validator_id,
            "reason_code": reason_code,
            "severity": severity,
            "public_summary": public_summary,
            "metrics": metrics or {},
        }
        self.events.append(event)
        return event
