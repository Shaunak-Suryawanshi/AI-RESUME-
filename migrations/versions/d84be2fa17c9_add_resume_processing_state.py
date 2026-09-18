"""add resume processing state

Revision ID: d84be2fa17c9
Revises: ab7e9c1d2f34
Create Date: 2026-09-18
"""
from alembic import op


revision = "d84be2fa17c9"
down_revision = "ab7e9c1d2f34"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("ck_resumes_processing_status", "resumes", type_="check")
    op.create_check_constraint(
        "ck_resumes_processing_status", "resumes",
        "processing_status IN ('pending', 'processing', 'completed', 'failed')",
    )


def downgrade():
    op.drop_constraint("ck_resumes_processing_status", "resumes", type_="check")
    op.create_check_constraint(
        "ck_resumes_processing_status", "resumes",
        "processing_status IN ('pending', 'completed', 'failed')",
    )
