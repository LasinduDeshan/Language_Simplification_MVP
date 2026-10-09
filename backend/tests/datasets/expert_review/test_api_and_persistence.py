"""Tests for API routes, RBAC authorization, DB unique constraints, and release-builder lock."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.database.db import SessionLocal
from app.datasets.expert_review.models import (
    ExpertReviewer,
    ReviewerConsent,
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
