"""
Unit tests for Preprocessing Accounting and Zero-Loss Reconciliation
"""
import os
import tempfile
from collections import namedtuple
from app.nlp_preprocessing.accounting import PreprocessingAccounting

MockInstance = namedtuple("MockInstance", ["text"])
MockRecord = namedtuple("MockRecord", ["processing_status"])

def test_preprocessing_accounting_zero_loss_balance():
    accounting = PreprocessingAccounting()
    
    # 5 raw text instances (with 1 duplicate text)
    raw_instances = [
        MockInstance(text="Hello world"),
        MockInstance(text="Hello world"),
        MockInstance(text="Good morning"),
        MockInstance(text="Test sentence"),
        MockInstance(text="Locked test item")
    ]
    
    # 5 processed records matching 1:1 with instances
    processed_records = [
        MockRecord(processing_status="success"),
        MockRecord(processing_status="success"),
        MockRecord(processing_status="fallback_success"),
        MockRecord(processing_status="manual_review_required"),
        MockRecord(processing_status="skipped_locked_test")
    ]
    
    parent_mappings = [
        {"parent_record_id": "P1", "text_instance_id": "T1"},
        {"parent_record_id": "P2", "text_instance_id": "T2"},
        {"parent_record_id": "P3", "text_instance_id": "T3"},
        {"parent_record_id": "P4", "text_instance_id": "T4"},
        {"parent_record_id": "P5", "text_instance_id": "T5"}
    ]
    
    summary = accounting.reconcile(raw_instances, processed_records, parent_mappings)
    
    assert summary["raw_text_instance_count"] == 5
    assert summary["unique_normalized_text_count"] == 4
    assert summary["duplicate_text_instance_count"] == 1
    assert summary["parent_text_mapping_count"] == 5
    assert summary["success_count"] == 2
    assert summary["fallback_success_count"] == 1
    assert summary["manual_review_count"] == 1
    assert summary["skipped_locked_test_count"] == 1
    assert summary["failed_count"] == 0
    assert summary["unaccounted_records"] == 0
    assert summary["is_zero_loss"] is True
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = os.path.join(tmpdir, "reconciliation.csv")
        accounting.generate_csv_report(summary, report_path)
        assert os.path.exists(report_path)
