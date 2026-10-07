"""Unit tests for LeakageGuard group and text hash isolation."""

from app.complexity_analysis.leakage_guard import LeakageGuard


def test_group_leakage_detected():
    train_recs = [{"source_group_id": "GRP-001"}, {"source_group_id": "GRP-002"}]
    val_recs = [{"source_group_id": "GRP-002"}, {"source_group_id": "GRP-003"}]

    clean, overlap = LeakageGuard.check_group_leakage(train_recs, val_recs)
    assert not clean
    assert "GRP-002" in overlap


def test_group_leakage_clean():
    train_recs = [{"source_group_id": "GRP-001"}, {"source_group_id": "GRP-002"}]
    val_recs = [{"source_group_id": "GRP-003"}, {"source_group_id": "GRP-004"}]

    clean, overlap = LeakageGuard.check_group_leakage(train_recs, val_recs)
    assert clean
    assert len(overlap) == 0


def test_hash_leakage_detected():
    train_recs = [{"text_hash": "HASH_A"}, {"text_hash": "HASH_B"}]
    val_recs = [{"text_hash": "HASH_B"}, {"text_hash": "HASH_C"}]

    clean, overlap = LeakageGuard.check_hash_leakage(train_recs, val_recs)
    assert not clean
    assert "HASH_B" in overlap


def test_locked_test_quarantine():
    recs = [
        {"dataset_split": "development_candidate_train", "text_hash": "HASH_1"},
        {"dataset_split": "development_candidate_test", "text_hash": "LOCKED_TEST_HASH"},
    ]
    clean, viols = LeakageGuard.check_locked_test_quarantine(recs)
    assert not clean
    assert len(viols) >= 1
