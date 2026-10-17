"""
Unit tests for Stage 36 protected storage, atomic operations, and cryptographic audit logging.
"""

import hashlib
import os
from pathlib import Path
import pytest

from app.sinhala_output_validation.storage import (
    CryptographicAuditLogger,
    ENV_PROTECTED_ROOT,
    PublicDiagnosticLogger,
    get_protected_storage_root,
    read_protected_content,
    write_protected_content,
)


@pytest.fixture
def temp_storage_root(tmp_path, monkeypatch):
    storage_dir = tmp_path / "protected_root"
    storage_dir.mkdir()
    monkeypatch.setenv(ENV_PROTECTED_ROOT, str(storage_dir))
    return storage_dir


class TestProtectedStorage:
    def test_write_and_read_protected_content(self, temp_storage_root):
        content = "නියමු සිංහල වාක්‍යයකි.".encode("utf-8")
        uri, sha256_hex = write_protected_content("candidates", "cand_001.txt", content)

        assert uri == "protected://candidates/cand_001.txt"
        assert sha256_hex == hashlib.sha256(content).hexdigest()

        # Read back
        read_bytes = read_protected_content(uri)
        assert read_bytes == content

    def test_write_with_expected_sha256_success(self, temp_storage_root):
        content = b"sample content"
        expected_hash = hashlib.sha256(content).hexdigest()
        uri, sha = write_protected_content("sources", "src_001.txt", content, expected_sha256=expected_hash)
        assert sha == expected_hash

    def test_write_with_expected_sha256_mismatch(self, temp_storage_root):
        content = b"sample content"
        wrong_hash = "0" * 64
        with pytest.raises(ValueError, match="Pre-write integrity failure"):
            write_protected_content("sources", "src_001.txt", content, expected_sha256=wrong_hash)

    def test_path_traversal_detection(self, temp_storage_root):
        with pytest.raises(ValueError, match="Path traversal detected"):
            write_protected_content("../escape", "hack.txt", b"evil")

        with pytest.raises(ValueError, match="Path traversal detected"):
            write_protected_content("sources", "../hack.txt", b"evil")

        with pytest.raises(ValueError, match="Filename '.*' cannot contain path separators"):
            write_protected_content("sources", "sub/hack.txt", b"evil")

    def test_read_invalid_uri_format(self, temp_storage_root):
        with pytest.raises(ValueError, match="must start with 'protected://'"):
            read_protected_content("file:///tmp/hack.txt")

        with pytest.raises(ValueError, match="must be of the form"):
            read_protected_content("protected://too/many/slashes/here.txt")

    def test_read_nonexistent_file(self, temp_storage_root):
        with pytest.raises(FileNotFoundError):
            read_protected_content("protected://candidates/missing.txt")


class TestCryptographicAuditLogger:
    def test_audit_log_signing_and_verification(self, temp_storage_root):
        logger = CryptographicAuditLogger(log_filename="test_audit.jsonl")

        logger.log_event("REQUEST_REGISTERED", {"request_id": "req_001", "candidate_id": "cand_001"})
        logger.log_event("VALIDATION_COMPLETED", {"request_id": "req_001", "disposition": "ACCEPTED"})

        is_valid, count, err = logger.verify_log_integrity()
        assert is_valid is True
        assert count == 2
        assert err is None

    def test_audit_log_tamper_detection(self, temp_storage_root):
        logger = CryptographicAuditLogger(log_filename="test_tamper.jsonl")
        logger.log_event("EVENT_1", {"data": 123})
        logger.log_event("EVENT_2", {"data": 456})

        # Tamper with file
        log_file = logger.log_path
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Modify first line payload
        tampered_line = lines[0].replace("123", "999")
        lines[0] = tampered_line

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        verifier = CryptographicAuditLogger(log_filename="test_tamper.jsonl")
        is_valid, count, err = verifier.verify_log_integrity()
        assert is_valid is False
        assert "HMAC signature mismatch" in err

    def test_audit_log_hash_chain_break_detection(self, temp_storage_root):
        logger = CryptographicAuditLogger(log_filename="test_chain.jsonl")
        logger.log_event("EVENT_1", {"data": 1})
        logger.log_event("EVENT_2", {"data": 2})
        logger.log_event("EVENT_3", {"data": 3})

        # Delete middle record
        log_file = logger.log_path
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Remove line 2 (EVENT_2)
        tampered_lines = [lines[0], lines[2]]
        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(tampered_lines)

        verifier = CryptographicAuditLogger(log_filename="test_chain.jsonl")
        is_valid, count, err = verifier.verify_log_integrity()
        assert is_valid is False
        assert ("Sequence gap" in err or "Hash-chain break" in err)


class TestPublicDiagnosticLogger:
    def test_public_diagnostic_sanitization(self):
        diag = PublicDiagnosticLogger()
        entry = diag.record_diagnostic(
            request_id="req_100",
            candidate_id="cand_100",
            validator_id="V3_PROTECTED_SPANS",
            reason_code="REJ_PROT_SPAN_MISSING",
            severity="CRITICAL",
            public_summary="Required numeric span [2024] was altered in output",
            metrics={"omitted_count": 1}
        )

        assert entry["request_id"] == "req_100"
        assert entry["reason_code"] == "REJ_PROT_SPAN_MISSING"
        assert "source_text" not in entry
        assert "candidate_text" not in entry
        assert len(diag.events) == 1
