"""stage12_boundaries

Revision ID: 91ee0a12abcd
Revises: 80ddb8f87777
Create Date: 2026-09-22 15:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from datetime import datetime

revision: str = '91ee0a12abcd'
down_revision: Union[str, Sequence[str], None] = '80ddb8f87777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update learner_profiles with Stage 12 fields
    with op.batch_alter_table("learner_profiles") as batch_op:
        batch_op.add_column(sa.Column("screening_risk_level", sa.String(length=20), nullable=True, server_default="moderate"))
        batch_op.add_column(sa.Column("recommended_support_level", sa.String(length=20), nullable=True, server_default="moderate"))
        batch_op.add_column(sa.Column("screening_source", sa.String(length=50), nullable=True, server_default="component_1"))
        batch_op.add_column(sa.Column("screening_version", sa.String(length=50), nullable=True, server_default="c1-1.0"))
        batch_op.add_column(sa.Column("screening_assessed_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("vocabulary_evidence_count", sa.Integer(), nullable=True, server_default="0"))
        batch_op.add_column(sa.Column("grammar_evidence_count", sa.Integer(), nullable=True, server_default="0"))
        batch_op.add_column(sa.Column("comprehension_evidence_count", sa.Integer(), nullable=True, server_default="0"))
        batch_op.add_column(sa.Column("instruction_evidence_count", sa.Integer(), nullable=True, server_default="0"))
        batch_op.add_column(sa.Column("performance_scoring_version", sa.String(length=20), nullable=True, server_default="1.0"))

    # Populate existing data: copy risk_support_level to screening_risk_level if present
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE learner_profiles 
        SET screening_risk_level = COALESCE(risk_support_level, 'moderate'),
            recommended_support_level = 'moderate',
            screening_source = 'component_1',
            screening_version = 'c1-1.0',
            screening_assessed_at = CURRENT_TIMESTAMP,
            vocabulary_evidence_count = 0,
            grammar_evidence_count = 0,
            comprehension_evidence_count = 0,
            instruction_evidence_count = 0,
            performance_scoring_version = '1.0'
        WHERE screening_risk_level IS NULL OR screening_risk_level = 'moderate'
    """))

    # 2. Update task_results with Stage 12 fields
    with op.batch_alter_table("task_results") as batch_op:
        batch_op.add_column(sa.Column("educational_summary_notes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("screening_risk_level", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("recommended_support_level", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("target_domain", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("evidence_count_before", sa.Integer(), nullable=True, server_default="0"))
        batch_op.add_column(sa.Column("evidence_count_after", sa.Integer(), nullable=True, server_default="1"))
        batch_op.add_column(sa.Column("score_update_applied", sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column("score_update_event_id", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("score_updated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("scoring_version", sa.String(length=20), nullable=True, server_default="1.0"))
        batch_op.add_column(sa.Column("calculation_snapshot", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("is_simulated", sa.Boolean(), nullable=True, server_default=sa.true()))
        batch_op.add_column(sa.Column("research_eligible", sa.Boolean(), nullable=True, server_default=sa.false()))

    # Copy legacy diagnostic_notes to educational_summary_notes
    conn.execute(sa.text("""
        UPDATE task_results 
        SET educational_summary_notes = diagnostic_notes,
            is_simulated = 1,
            research_eligible = 0,
            scoring_version = '1.0'
        WHERE educational_summary_notes IS NULL AND diagnostic_notes IS NOT NULL
    """))


def downgrade() -> None:
    with op.batch_alter_table("task_results") as batch_op:
        batch_op.drop_column("research_eligible")
        batch_op.drop_column("is_simulated")
        batch_op.drop_column("calculation_snapshot")
        batch_op.drop_column("scoring_version")
        batch_op.drop_column("score_updated_at")
        batch_op.drop_column("score_update_event_id")
        batch_op.drop_column("score_update_applied")
        batch_op.drop_column("evidence_count_after")
        batch_op.drop_column("evidence_count_before")
        batch_op.drop_column("target_domain")
        batch_op.drop_column("recommended_support_level")
        batch_op.drop_column("screening_risk_level")
        batch_op.drop_column("educational_summary_notes")

    with op.batch_alter_table("learner_profiles") as batch_op:
        batch_op.drop_column("performance_scoring_version")
        batch_op.drop_column("instruction_evidence_count")
        batch_op.drop_column("comprehension_evidence_count")
        batch_op.drop_column("grammar_evidence_count")
        batch_op.drop_column("vocabulary_evidence_count")
        batch_op.drop_column("screening_assessed_at")
        batch_op.drop_column("screening_version")
        batch_op.drop_column("screening_source")
        batch_op.drop_column("recommended_support_level")
        batch_op.drop_column("screening_risk_level")
