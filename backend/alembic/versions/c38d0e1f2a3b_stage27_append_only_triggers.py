"""stage27 append only triggers and reviewer separation guards

Revision ID: c38d0e1f2a3b
Revises: b27c9d0e1f2a
Create Date: 2026-10-10 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c38d0e1f2a3b'
down_revision = 'b27c9d0e1f2a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Sealed submissions immutability triggers
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_sealed_submission_update
    BEFORE UPDATE ON expert_review_submissions
    FOR EACH ROW
    WHEN OLD.is_sealed = 1
    BEGIN
        SELECT RAISE(ABORT, 'Cannot update sealed review submission');
    END;
    """)

    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_sealed_submission_delete
    BEFORE DELETE ON expert_review_submissions
    FOR EACH ROW
    WHEN OLD.is_sealed = 1
    BEGIN
        SELECT RAISE(ABORT, 'Cannot delete sealed review submission');
    END;
    """)

    # 2. Append-only audit log triggers
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_log_update
    BEFORE UPDATE ON expert_review_audit_log
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: updates not allowed');
    END;
    """)

    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_audit_log_delete
    BEFORE DELETE ON expert_review_audit_log
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: deletions not allowed');
    END;
    """)

    # 3. Adjudication records immutability triggers
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_adjudication_update
    BEFORE UPDATE ON expert_adjudications
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Adjudication records are immutable: updates not allowed');
    END;
    """)

    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_adjudication_delete
    BEFORE DELETE ON expert_adjudications
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Adjudication records are immutable: deletions not allowed');
    END;
    """)

    # 4. Release approval immutability triggers
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_release_approval_update
    BEFORE UPDATE ON expert_release_approvals
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Release approvals are immutable: updates not allowed');
    END;
    """)

    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_release_approval_delete
    BEFORE DELETE ON expert_release_approvals
    FOR EACH ROW
    BEGIN
        SELECT RAISE(ABORT, 'Release approvals are immutable: deletions not allowed');
    END;
    """)

    # 5. Distinct Reviewer A and Reviewer B batch enforcement triggers
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_batch
    BEFORE INSERT ON expert_review_batches
    FOR EACH ROW
    WHEN NEW.reviewer_a_id = NEW.reviewer_b_id
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """)

    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_batch_upd
    BEFORE UPDATE ON expert_review_batches
    FOR EACH ROW
    WHEN NEW.reviewer_a_id = NEW.reviewer_b_id
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """)

    # 6. Distinct Reviewer A and Reviewer B dual assignment guard on same record
    op.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_prevent_same_reviewer_dual_assignment
    BEFORE INSERT ON expert_review_assignments
    FOR EACH ROW
    WHEN EXISTS (
        SELECT 1 FROM expert_review_assignments
        WHERE record_id = NEW.record_id
          AND review_round = NEW.review_round
          AND reviewer_id = NEW.reviewer_id
    )
    BEGIN
        SELECT RAISE(ABORT, 'Reviewer A and Reviewer B must be different people');
    END;
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_same_reviewer_dual_assignment;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_same_reviewer_batch_upd;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_same_reviewer_batch;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_release_approval_delete;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_release_approval_update;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_adjudication_delete;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_adjudication_update;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_audit_log_delete;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_audit_log_update;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_sealed_submission_delete;")
    op.execute("DROP TRIGGER IF EXISTS trg_prevent_sealed_submission_update;")
