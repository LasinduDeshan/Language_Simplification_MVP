"""Tests for API routes, RBAC authorization, DB unique constraints, and release-builder lock."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.database.db import SessionLocal
from app.datasets.expert_review.models import (
    ExpertReviewer,
    ReviewerConsent,
    ExpertReviewBatch,
    ExpertReviewAssignment,
    ExpertReviewSubmission,
    ExpertAdjudicationCase,
    ExpertReviewAuditLog,
)
from app.api.v1.endpoints.expert_review import reviewer_registry, assignment_service, repo
from app.datasets.expert_review.schemas import (
    ReviewManifestItem,
    ReviewRecordType,
    SupportLevel,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database.db import Base
    import app.database.models  # ensure models registered on Base.metadata

    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_api_auth_required(client):
    """Missing X-Reviewer-Id header results in 401 Unauthorized."""
    resp = client.get("/api/v1/expert-review/batches")
    assert resp.status_code == 401
    assert "Authentication required" in resp.json()["detail"]


def test_api_revoked_reviewer_rejected(client):
    """Revoked reviewer account is denied access with 403 Forbidden."""
    reviewer_registry.register_reviewer(
        reviewer_id="REV-REVOKED-01",
        full_name="Revoked Reviewer",
        account_status="revoked",
    )

    resp = client.get(
        "/api/v1/expert-review/batches",
        headers={"X-Reviewer-Id": "REV-REVOKED-01"},
    )
    assert resp.status_code == 403
    assert "revoked" in resp.json()["detail"]


def test_api_adjudicator_role_required_for_disagreements(client):
    """Normal reviewer cannot access /disagreements queue; Adjudicator can."""
    # Standard reviewer -> 403
    resp = client.get(
        "/api/v1/expert-review/disagreements",
        headers={"X-Reviewer-Id": "REV-01", "X-Reviewer-Role": "reviewer"},
    )
    assert resp.status_code == 403
    assert "Adjudicator privileges required" in resp.json()["detail"]

    # Adjudicator -> 200
    resp_adj = client.get(
        "/api/v1/expert-review/disagreements",
        headers={"X-Reviewer-Id": "ADJ-01", "X-Reviewer-Role": "adjudicator"},
    )
    assert resp_adj.status_code == 200
    assert "unresolved_count" in resp_adj.json()


def test_api_release_builder_admin_only_and_lock_check(client):
    """Non-admin cannot build release; Admin receives lock response when reviews are incomplete."""
    # Reviewer attempting build -> 403
    resp_rev = client.post(
        "/api/v1/expert-review/releases/build",
        headers={"X-Reviewer-Id": "REV-01", "X-Reviewer-Role": "reviewer"},
        json={"force_build": False, "signoff_name": "Test"},
    )
    assert resp_rev.status_code == 403

    # Admin attempting build without complete review -> RELEASE_BLOCKED_INCOMPLETE_EXPERT_REVIEW
    resp_admin = client.post(
        "/api/v1/expert-review/releases/build",
        headers={"X-Reviewer-Id": "ADMIN-01", "X-Reviewer-Role": "admin"},
        json={"force_build": False, "signoff_name": "Admin Lead"},
    )
    assert resp_admin.status_code == 200
    data = resp_admin.json()
    assert data["status"] == "RELEASE_BLOCKED_INCOMPLETE_EXPERT_REVIEW"
    assert "locked" in data["reason"]


def test_database_level_idempotency_constraints(db_session):
    """Tests DB uniqueness constraints to ensure concurrent duplicate protection."""
    # Ensure test reviewer exists
    reviewer = db_session.query(ExpertReviewer).filter_by(reviewer_id="REV-DB-TEST-01").first()
    if not reviewer:
        reviewer = ExpertReviewer(
            reviewer_id="REV-DB-TEST-01",
            full_name="DB Test Reviewer",
            qualification_category="Linguistics",
            qualification_tracks=["Track 1"],
            account_status="active",
        )
        db_session.add(reviewer)
        db_session.commit()

    # 1. Assignment unique constraint: UNIQUE(assignment_id, reviewer_role)
    asg1 = ExpertReviewAssignment(
        assignment_id="ASG-UNIQUE-01",
        batch_id="BATCH-01",
        record_id="SIMP-EN-000001",
        reviewer_id="REV-DB-TEST-01",
        reviewer_role="reviewer_a",
    )
    db_session.add(asg1)
    db_session.commit()

    asg_dup = ExpertReviewAssignment(
        assignment_id="ASG-UNIQUE-01",
        batch_id="BATCH-01",
        record_id="SIMP-EN-000002",
        reviewer_id="REV-DB-TEST-01",
        reviewer_role="reviewer_a",  # Duplicate (assignment_id, reviewer_role)
    )
    db_session.add(asg_dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 2. Submission unique constraint: UNIQUE(reviewer_id, record_id, review_round)
    sub1 = ExpertReviewSubmission(
        submission_id="SUB-UNIQUE-01",
        record_id="SIMP-EN-000001",
        reviewer_id="REV-DB-TEST-01",
        batch_id="BATCH-01",
        review_round=1,
        taxonomy_class="text_simplification",
        ratings={"meaning_preservation": 5},
        critical_checks={},
        workflow_flags={},
        provisional_disposition="expert_approved",
        submission_hash="hash-sub-1",
        is_sealed=True,
    )
    db_session.add(sub1)
    db_session.commit()

    sub_dup = ExpertReviewSubmission(
        submission_id="SUB-UNIQUE-02",
        record_id="SIMP-EN-000001",
        reviewer_id="REV-DB-TEST-01",  # Same reviewer, same record, same round
        batch_id="BATCH-01",
        review_round=1,
        taxonomy_class="text_simplification",
        ratings={"meaning_preservation": 5},
        critical_checks={},
        workflow_flags={},
        provisional_disposition="expert_approved",
        submission_hash="hash-sub-2",
        is_sealed=True,
    )
    db_session.add(sub_dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_append_only_audit_log_persistence(db_session):
    """Verifies that audit log entries are persisted with immutable hashes and timestamps."""
    event = ExpertReviewAuditLog(
        event_id="EVT-000001",
        event_type="submission_sealed",
        actor_id="REV-01",
        record_id="SIMP-EN-000001",
        details={"status": "sealed", "disposition": "expert_approved"},
        event_hash="audit_sha256_hash",
    )
    db_session.add(event)
    db_session.commit()

    saved = db_session.query(ExpertReviewAuditLog).filter_by(event_id="EVT-000001").first()
    assert saved is not None
    assert saved.event_type == "submission_sealed"
    assert saved.event_hash == "audit_sha256_hash"


def test_sealed_submission_db_trigger_prevents_update_and_delete(db_session):
    """Direct SQL UPDATE or DELETE on sealed submissions is rejected by database triggers."""
    from sqlalchemy import text
    from sqlalchemy.exc import DatabaseError

    # 1. Ensure a sealed submission exists
    sub = db_session.query(ExpertReviewSubmission).filter_by(submission_id="SUB-TRIGGER-01").first()
    if not sub:
        sub = ExpertReviewSubmission(
            submission_id="SUB-TRIGGER-01",
            record_id="SIMP-EN-000999",
            reviewer_id="REV-DB-TEST-01",
            batch_id="BATCH-01",
            review_round=1,
            taxonomy_class="text_simplification",
            ratings={"meaning_preservation": 5},
            critical_checks={},
            workflow_flags={},
            provisional_disposition="expert_approved",
            submission_hash="hash-sub-trg-1",
            is_sealed=True,
        )
        db_session.add(sub)
        db_session.commit()

    # 2. Direct raw SQL UPDATE must be aborted by database trigger
    with pytest.raises(DatabaseError) as exc_info:
        db_session.execute(
            text("UPDATE expert_review_submissions SET reviewer_notes = 'tampered' WHERE submission_id = 'SUB-TRIGGER-01'")
        )
        db_session.commit()
    assert "Cannot update sealed review submission" in str(exc_info.value)
    db_session.rollback()

    # 3. Direct raw SQL DELETE must be aborted by database trigger
    with pytest.raises(DatabaseError) as exc_info:
        db_session.execute(
            text("DELETE FROM expert_review_submissions WHERE submission_id = 'SUB-TRIGGER-01'")
        )
        db_session.commit()
    assert "Cannot delete sealed review submission" in str(exc_info.value)
    db_session.rollback()

    # 4. ORM level update/delete is also blocked
    sub_orm = db_session.query(ExpertReviewSubmission).filter_by(submission_id="SUB-TRIGGER-01").first()
    sub_orm.reviewer_notes = "orm_tamper"
    with pytest.raises(ValueError) as exc_info:
        db_session.commit()
    assert "Cannot update sealed review submission" in str(exc_info.value)
    db_session.rollback()

    sub_orm = db_session.query(ExpertReviewSubmission).filter_by(submission_id="SUB-TRIGGER-01").first()
    db_session.delete(sub_orm)
    with pytest.raises(ValueError) as exc_info:
        db_session.commit()
    assert "Cannot delete sealed review submission" in str(exc_info.value)
    db_session.rollback()


def test_audit_log_and_adjudications_immutable_triggers(db_session):
    """Database triggers enforce append-only immutability on audit logs and adjudications."""
    from sqlalchemy import text
    from sqlalchemy.exc import DatabaseError

    # 1. Ensure an audit log event exists
    event = ExpertReviewAuditLog(
        event_id="EVT-TRIGGER-01",
        event_type="submission_sealed",
        actor_id="REV-01",
        record_id="SIMP-EN-000001",
        details={"status": "sealed"},
        event_hash="audit_hash_test",
    )
    db_session.add(event)
    db_session.commit()

    # Direct raw SQL UPDATE on audit log -> rejected by database trigger
    with pytest.raises(DatabaseError) as exc_info:
        db_session.execute(
            text("UPDATE expert_review_audit_log SET actor_id = 'hacker' WHERE event_id = 'EVT-TRIGGER-01'")
        )
        db_session.commit()
    assert "Audit log is append-only" in str(exc_info.value)
    db_session.rollback()

    # Direct raw SQL DELETE on audit log -> rejected by database trigger
    with pytest.raises(DatabaseError) as exc_info:
        db_session.execute(
            text("DELETE FROM expert_review_audit_log WHERE event_id = 'EVT-TRIGGER-01'")
        )
        db_session.commit()
    assert "Audit log is append-only" in str(exc_info.value)
    db_session.rollback()


def test_distinct_reviewer_enforcement_on_batch_and_assignments(db_session):
    """Database enforces that Reviewer A and Reviewer B must be different individuals."""
    from sqlalchemy.exc import DatabaseError, IntegrityError

    # 1. Batch cannot have reviewer_a_id == reviewer_b_id
    invalid_batch = ExpertReviewBatch(
        batch_id="BATCH-INVALID-SAME-REV",
        reviewer_panel_id="PANEL-INVALID",
        reviewer_a_id="REV-DB-TEST-01",
        reviewer_b_id="REV-DB-TEST-01",  # Same reviewer!
    )
    db_session.add(invalid_batch)
    with pytest.raises((IntegrityError, DatabaseError)) as exc_info:
        db_session.commit()
    assert "Reviewer A and Reviewer B must be different people" in str(exc_info.value) or "ck_batch_distinct_reviewers" in str(exc_info.value)
    db_session.rollback()

    # 2. Assignment uniqueness prevents same reviewer having both roles for same record
    asg_a = ExpertReviewAssignment(
        assignment_id="ASG-DUAL-01",
        batch_id="BATCH-01",
        record_id="SIMP-EN-000555",
        reviewer_id="REV-DB-TEST-01",
        reviewer_role="reviewer_a",
        review_round=1,
    )
    db_session.add(asg_a)
    db_session.commit()

    asg_b_same = ExpertReviewAssignment(
        assignment_id="ASG-DUAL-02",
        batch_id="BATCH-01",
        record_id="SIMP-EN-000555",
        reviewer_id="REV-DB-TEST-01",  # Same reviewer trying to take reviewer_b role!
        reviewer_role="reviewer_b",
        review_round=1,
    )
    db_session.add(asg_b_same)
    with pytest.raises((IntegrityError, DatabaseError)) as exc_info:
        db_session.commit()
    assert "uq_reviewer_record_round" in str(exc_info.value) or "Reviewer A and Reviewer B must be different people" in str(exc_info.value)
    db_session.rollback()

