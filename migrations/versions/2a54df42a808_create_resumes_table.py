"""create resumes table

Revision ID: 2a54df42a808
Revises: 8bb973b191a1
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa


revision = "2a54df42a808"
down_revision = "8bb973b191a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"], unique=False)


def downgrade():
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")
