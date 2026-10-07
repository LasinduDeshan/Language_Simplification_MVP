"""stage15_quality_validation_tables

Revision ID: a15b8c9d0e1f
Revises: 91ee0a12abcd
Create Date: 2026-09-24 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a15b8c9d0e1f'
down_revision: Union[str, Sequence[str], None] = '91ee0a12abcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. dataset_validation_runs table
    op.create_table(
        'dataset_validation_runs',
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_layer', sa.String(length=64), nullable=False),
        sa.Column('dataset_version', sa.String(length=32), nullable=False, server_default='0.1.0'),
        sa.Column('quality_rule_set_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='queued'),
        sa.Column('total_records', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('review_required_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quarantined_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('created_by', sa.String(length=64), nullable=False, server_default='system_validator'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('run_id')
    )
    op.create_index('ix_dataset_validation_runs_run_id', 'dataset_validation_runs', ['run_id'])
    op.create_index('ix_dataset_validation_runs_dataset_layer', 'dataset_validation_runs', ['dataset_layer'])
    op.create_index('ix_dataset_validation_runs_status', 'dataset_validation_runs', ['status'])
    op.create_index('ix_dataset_validation_runs_idempotency_key', 'dataset_validation_runs', ['idempotency_key'], unique=True)

    # 2. dataset_quality_rule_results table
    op.create_table(
        'dataset_quality_rule_results',
        sa.Column('result_id', sa.String(length=64), nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_layer', sa.String(length=64), nullable=False),
        sa.Column('rule_id', sa.String(length=64), nullable=False),
        sa.Column('rule_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('validator_name', sa.String(length=128), nullable=False),
        sa.Column('validator_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('severity', sa.String(length=32), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('threshold', sa.String(length=64), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['run_id'], ['dataset_validation_runs.run_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('result_id')
    )
    op.create_index('ix_dataset_quality_rule_results_result_id', 'dataset_quality_rule_results', ['result_id'])
    op.create_index('ix_dataset_quality_rule_results_run_id', 'dataset_quality_rule_results', ['run_id'])
    op.create_index('ix_dataset_quality_rule_results_record_id', 'dataset_quality_rule_results', ['record_id'])
    op.create_index('ix_dataset_quality_rule_results_dataset_layer', 'dataset_quality_rule_results', ['dataset_layer'])
    op.create_index('ix_dataset_quality_rule_results_rule_id', 'dataset_quality_rule_results', ['rule_id'])

    # 3. dataset_record_quality_summaries table
    op.create_table(
        'dataset_record_quality_summaries',
        sa.Column('summary_id', sa.String(length=64), nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_layer', sa.String(length=64), nullable=False),
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('quality_rule_set_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('quality_status', sa.String(length=64), nullable=False),
        sa.Column('overall_quality_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('dimension_scores', sa.JSON(), nullable=True),
        sa.Column('rules_executed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rules_passed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('warnings_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('critical_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('requires_expert_review', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('research_eligible', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('approved_for_child_delivery', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('validated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['run_id'], ['dataset_validation_runs.run_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('summary_id')
    )
    op.create_index('ix_dataset_record_quality_summaries_summary_id', 'dataset_record_quality_summaries', ['summary_id'])
    op.create_index('ix_dataset_record_quality_summaries_run_id', 'dataset_record_quality_summaries', ['run_id'])
    op.create_index('ix_dataset_record_quality_summaries_record_id', 'dataset_record_quality_summaries', ['record_id'])
    op.create_index('ix_dataset_record_quality_summaries_dataset_layer', 'dataset_record_quality_summaries', ['dataset_layer'])
    op.create_index('ix_dataset_record_quality_summaries_quality_status', 'dataset_record_quality_summaries', ['quality_status'])

    # 4. dataset_manual_review_queue table
    op.create_table(
        'dataset_manual_review_queue',
        sa.Column('entry_id', sa.String(length=64), nullable=False),
        sa.Column('run_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_layer', sa.String(length=64), nullable=False),
        sa.Column('priority', sa.String(length=32), nullable=False, server_default='medium'),
        sa.Column('triggering_rule_ids', sa.JSON(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('recommended_review_type', sa.String(length=64), nullable=False, server_default='linguistic_triage'),
        sa.Column('review_status', sa.String(length=64), nullable=False, server_default='pending'),
        sa.Column('assigned_reviewer_id', sa.String(length=64), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['dataset_validation_runs.run_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('entry_id')
    )
    op.create_index('ix_dataset_manual_review_queue_entry_id', 'dataset_manual_review_queue', ['entry_id'])
    op.create_index('ix_dataset_manual_review_queue_run_id', 'dataset_manual_review_queue', ['run_id'])
    op.create_index('ix_dataset_manual_review_queue_record_id', 'dataset_manual_review_queue', ['record_id'])
    op.create_index('ix_dataset_manual_review_queue_dataset_layer', 'dataset_manual_review_queue', ['dataset_layer'])
    op.create_index('ix_dataset_manual_review_queue_priority', 'dataset_manual_review_queue', ['priority'])
    op.create_index('ix_dataset_manual_review_queue_review_status', 'dataset_manual_review_queue', ['review_status'])

    # 5. dataset_record_revisions table
    op.create_table(
        'dataset_record_revisions',
        sa.Column('revision_id', sa.String(length=64), nullable=False),
        sa.Column('record_id', sa.String(length=64), nullable=False),
        sa.Column('dataset_layer', sa.String(length=64), nullable=False),
        sa.Column('parent_revision_id', sa.String(length=64), nullable=True),
        sa.Column('previous_content', sa.JSON(), nullable=False),
        sa.Column('corrected_content', sa.JSON(), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('revalidated', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('revalidation_run_id', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('revision_id')
    )
    op.create_index('ix_dataset_record_revisions_revision_id', 'dataset_record_revisions', ['revision_id'])
    op.create_index('ix_dataset_record_revisions_record_id', 'dataset_record_revisions', ['record_id'])
    op.create_index('ix_dataset_record_revisions_dataset_layer', 'dataset_record_revisions', ['dataset_layer'])


def downgrade() -> None:
    op.drop_table('dataset_record_revisions')
    op.drop_table('dataset_manual_review_queue')
    op.drop_table('dataset_record_quality_summaries')
    op.drop_table('dataset_quality_rule_results')
    op.drop_table('dataset_validation_runs')
