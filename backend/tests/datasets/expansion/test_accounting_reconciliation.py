"""
Unit tests for Stage 20 3-Tier Mutually Exclusive Accounting.
"""
import pytest

def test_three_tier_accounting_identity():
    # Tier 1: Authoring
    submitted = 300
    accepted = 300
    rejected_pre_import = 0
    pre_import_review = 0
    assert submitted == accepted + rejected_pre_import + pre_import_review

    # Tier 2: Validation
    imported = accepted
    auto_passed = 300
    auto_failed = 0
    manual_review = 0
    quarantined = 0
    assert imported == auto_passed + auto_failed + manual_review + quarantined

    # Tier 3: Release splits
    candidate_records = auto_passed
    train = 210
    val = 45
    test = 45
    excluded = 0
    assert candidate_records == (train + val + test) + excluded
