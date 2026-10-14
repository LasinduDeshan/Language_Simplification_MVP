"""
Tests verifying the NO_SCHEMA_CHANGE_REQUIRED decision and audit record integrity.
"""
import json
import hashlib
from pathlib import Path

def test_no_schema_change_decision_record():
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    report_path = repo_root / "docs" / "stage29_database_migration_or_no_change_report.md"
    audit_path = repo_root / "docs" / "stage29_unicode_storage_audit.md"

    assert report_path.exists(), "Decision report docs/stage29_database_migration_or_no_change_report.md must exist"
    assert audit_path.exists(), "Audit report docs/stage29_unicode_storage_audit.md must exist"

    # Compute actual audit hash
    actual_audit_hash = hashlib.sha256(audit_path.read_bytes()).hexdigest()

    report_content = report_path.read_text(encoding="utf-8")
    assert "NO_SCHEMA_CHANGE_REQUIRED" in report_content
    assert "SQLite" in report_content
    assert actual_audit_hash in report_content, f"Evidence hash {actual_audit_hash} must be referenced in decision report"
