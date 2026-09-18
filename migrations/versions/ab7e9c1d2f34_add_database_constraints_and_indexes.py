"""add database constraints and indexes

Revision ID: ab7e9c1d2f34
Revises: f0298a5b1c4d
Create Date: 2026-09-18
"""
from alembic import op


revision = "ab7e9c1d2f34"
down_revision = "f0298a5b1c4d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "ck_resumes_processing_status", "resumes",
        "processing_status IN ('pending', 'completed', 'failed')",
    )
    op.create_check_constraint(
        "ck_jobs_processing_status", "jobs",
        "processing_status IN ('pending', 'completed', 'failed')",
    )
    op.create_check_constraint(
        "ck_analyses_match_score", "analyses", "match_score >= 0 AND match_score <= 100",
    )
    op.create_check_constraint(
        "ck_analyses_ai_status", "analyses",
        "ai_status IN ('not_requested', 'pending', 'completed', 'failed')",
    )
    op.create_index("ix_resumes_user_created_at", "resumes", ["user_id", "created_at"], unique=False)
    op.create_index("ix_jobs_user_created_at", "jobs", ["user_id", "created_at"], unique=False)
    op.create_index("ix_analyses_user_created_at", "analyses", ["user_id", "created_at"], unique=False)


def downgrade():
    op.drop_index("ix_analyses_user_created_at", table_name="analyses")
    op.drop_index("ix_jobs_user_created_at", table_name="jobs")
    op.drop_index("ix_resumes_user_created_at", table_name="resumes")
    op.drop_constraint("ck_analyses_ai_status", "analyses", type_="check")
    op.drop_constraint("ck_analyses_match_score", "analyses", type_="check")
    op.drop_constraint("ck_jobs_processing_status", "jobs", type_="check")
    op.drop_constraint("ck_resumes_processing_status", "resumes", type_="check")
