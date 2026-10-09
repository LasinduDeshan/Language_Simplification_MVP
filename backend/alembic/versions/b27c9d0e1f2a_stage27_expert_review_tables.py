"""stage27_expert_review_tables

Revision ID: b27c9d0e1f2a
Revises: a15b8c9d0e1f
Create Date: 2026-10-09 23:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b27c9d0e1f2a'
down_revision: Union[str, Sequence[str], None] = 'a15b8c9d0e1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. expert_reviewers
    op.create_table(
        'expert_reviewers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('reviewer_id', sa.String(length=50), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='reviewer'),
        sa.Column('qualification_category', sa.String(length=100), nullable=False),
        sa.Column('qualification_tracks', sa.JSON(), nullable=False),
        sa.Column('relevant_experience_years', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('calibration_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('calibration_agreement_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('account_status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reviewer_id')
    )
    op.create_index('ix_expert_reviewers_reviewer_id', 'expert_reviewers', ['reviewer_id'])

    # 2. expert_reviewer_consents
    op.create_table(
        'expert_reviewer_consents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('reviewer_id', sa.String(length=50), nullable=False),
        sa.Column('participation_agreement_signed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('confidentiality_undertaking_signed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('conflict_of_interest_declared', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('coi_details', sa.Text(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('ip_or_signature_hash', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['expert_reviewers.reviewer_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_expert_reviewer_consents_reviewer_id', 'expert_reviewer_consents', ['reviewer_id'])

    # 3. expert_review_batches
    op.create_table(
        'expert_review_batches',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('batch_id', sa.String(length=50), nullable=False),
        sa.Column('reviewer_panel_id', sa.String(length=50), nullable=False),
        sa.Column('reviewer_a_id', sa.String(length=50), nullable=False),
        sa.Column('reviewer_b_id', sa.String(length=50), nullable=False),
        sa.Column('item_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='assigned'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('batch_id')
    )
    op.create_index('ix_expert_review_batches_batch_id', 'expert_review_batches', ['batch_id'])

    # 4. expert_review_assignments
    op.create_table(
        'expert_review_assignments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('assignment_id', sa.String(length=64), nullable=False),
        sa.Column('batch_id', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('reviewer_id', sa.String(length=50), nullable=False),
        sa.Column('reviewer_role', sa.String(length=20), nullable=False),
        sa.Column('review_round', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='assigned'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reviewer_id'], ['expert_reviewers.reviewer_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('assignment_id', 'reviewer_role', name='uq_assignment_role'),
        sa.UniqueConstraint('reviewer_id', 'record_id', 'review_round', name='uq_reviewer_record_round')
    )
    op.create_index('ix_expert_review_assignments_assignment_id', 'expert_review_assignments', ['assignment_id'])
    op.create_index('ix_expert_review_assignments_batch_id', 'expert_review_assignments', ['batch_id'])
    op.create_index('ix_expert_review_assignments_record_id', 'expert_review_assignments', ['record_id'])
    op.create_index('ix_expert_review_assignments_reviewer_id', 'expert_review_assignments', ['reviewer_id'])

    # 5. expert_review_submissions
    op.create_table(
        'expert_review_submissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('submission_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('reviewer_id', sa.String(length=50), nullable=False),
        sa.Column('batch_id', sa.String(length=50), nullable=False),
        sa.Column('review_round', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('taxonomy_class', sa.String(length=50), nullable=False),
        sa.Column('ratings', sa.JSON(), nullable=False),
        sa.Column('critical_checks', sa.JSON(), nullable=False),
        sa.Column('workflow_flags', sa.JSON(), nullable=False),
        sa.Column('support_tier_review', sa.JSON(), nullable=True),
        sa.Column('lexicon_disposition', sa.String(length=50), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('provisional_disposition', sa.String(length=50), nullable=False),
        sa.Column('submission_hash', sa.String(length=64), nullable=False),
        sa.Column('is_sealed', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reviewer_id'], ['expert_reviewers.reviewer_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('submission_id'),
        sa.UniqueConstraint('submission_hash'),
        sa.UniqueConstraint('reviewer_id', 'record_id', 'review_round', name='uq_sub_reviewer_record_round')
    )
    op.create_index('ix_expert_review_submissions_submission_id', 'expert_review_submissions', ['submission_id'])
    op.create_index('ix_expert_review_submissions_record_id', 'expert_review_submissions', ['record_id'])
    op.create_index('ix_expert_review_submissions_reviewer_id', 'expert_review_submissions', ['reviewer_id'])

    # 6. expert_adjudications
    op.create_table(
        'expert_adjudications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('adjudication_case_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('adjudicator_id', sa.String(length=50), nullable=False),
        sa.Column('resolution_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reviewer_a_submission_id', sa.String(length=64), nullable=False),
        sa.Column('reviewer_b_submission_id', sa.String(length=64), nullable=False),
        sa.Column('conflict_reasons', sa.JSON(), nullable=False),
        sa.Column('final_taxonomy_class', sa.String(length=50), nullable=False),
        sa.Column('final_disposition', sa.String(length=50), nullable=False),
        sa.Column('adjudicated_critical_checks', sa.JSON(), nullable=False),
        sa.Column('adjudicated_ratings', sa.JSON(), nullable=True),
        sa.Column('decision_rationale', sa.Text(), nullable=False),
        sa.Column('revision_required', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('adjudicated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['adjudicator_id'], ['expert_reviewers.reviewer_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('adjudication_case_id', 'resolution_version', name='uq_adj_case_version')
    )
    op.create_index('ix_expert_adjudications_adjudication_case_id', 'expert_adjudications', ['adjudication_case_id'])
    op.create_index('ix_expert_adjudications_record_id', 'expert_adjudications', ['record_id'])

    # 7. expert_revisions
    op.create_table(
        'expert_revisions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('revision_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('source_group_id', sa.String(length=64), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('revised_text', sa.Text(), nullable=False),
        sa.Column('original_hash', sa.String(length=64), nullable=False),
        sa.Column('revised_hash', sa.String(length=64), nullable=False),
        sa.Column('revision_reason', sa.Text(), nullable=False),
        sa.Column('revised_by', sa.String(length=50), nullable=False),
        sa.Column('stage14_schema_validation', sa.String(length=20), nullable=False, server_default='PASSED'),
        sa.Column('stage15_quality_validation', sa.String(length=20), nullable=False, server_default='PASSED'),
        sa.Column('final_disposition', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('revision_id')
    )
    op.create_index('ix_expert_revisions_revision_id', 'expert_revisions', ['revision_id'])
    op.create_index('ix_expert_revisions_record_id', 'expert_revisions', ['record_id'])

    # 8. expert_review_audit_log (append-only)
    op.create_table(
        'expert_review_audit_log',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('ix_expert_review_audit_log_event_id', 'expert_review_audit_log', ['event_id'])

    # 9. expert_release_approvals
    op.create_table(
        'expert_release_approvals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('release_version', sa.String(length=20), nullable=False),
        sa.Column('approved_by', sa.String(length=50), nullable=False),
        sa.Column('signoff_role', sa.String(length=50), nullable=False),
        sa.Column('unresolved_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unaccounted_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('immutability_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('approved_for_stage28_evaluation', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('approved_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('release_version')
    )


def downgrade() -> None:
    op.drop_table('expert_release_approvals')
    op.drop_table('expert_review_audit_log')
    op.drop_table('expert_revisions')
    op.drop_table('expert_adjudications')
    op.drop_table('expert_review_submissions')
    op.drop_table('expert_review_assignments')
    op.drop_table('expert_review_batches')
    op.drop_table('expert_reviewer_consents')
    op.drop_table('expert_reviewers')
