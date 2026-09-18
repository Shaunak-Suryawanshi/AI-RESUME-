"""add resume processing fields

Revision ID: 6e1caaeb91c0
Revises: 2a54df42a808
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa


revision = "6e1caaeb91c0"
down_revision = "2a54df42a808"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("resumes", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("resumes", sa.Column("sections", sa.JSON(), nullable=True))
    op.add_column("resumes", sa.Column("skills", sa.JSON(), nullable=True))
    op.add_column(
        "resumes",
        sa.Column("processing_status", sa.String(length=20), server_default="pending", nullable=False),
    )
    op.add_column("resumes", sa.Column("processing_error", sa.String(length=500), nullable=True))
    op.add_column("resumes", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("resumes", "processed_at")
    op.drop_column("resumes", "processing_error")
    op.drop_column("resumes", "processing_status")
    op.drop_column("resumes", "skills")
    op.drop_column("resumes", "sections")
    op.drop_column("resumes", "extracted_text")
