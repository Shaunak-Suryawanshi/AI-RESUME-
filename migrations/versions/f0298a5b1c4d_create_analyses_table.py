"""create analyses table

Revision ID: f0298a5b1c4d
Revises: c719b8b1e3d2
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa


revision = "f0298a5b1c4d"
down_revision = "c719b8b1e3d2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("matching_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.Column("ai_feedback", sa.JSON(), nullable=True),
        sa.Column("ai_status", sa.String(length=20), server_default="not_requested", nullable=False),
        sa.Column("ai_error", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"], unique=False)
    op.create_index("ix_analyses_resume_id", "analyses", ["resume_id"], unique=False)
    op.create_index("ix_analyses_job_id", "analyses", ["job_id"], unique=False)


def downgrade():
    op.drop_index("ix_analyses_job_id", table_name="analyses")
    op.drop_index("ix_analyses_resume_id", table_name="analyses")
    op.drop_index("ix_analyses_user_id", table_name="analyses")
    op.drop_table("analyses")
