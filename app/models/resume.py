from sqlalchemy.sql import func

from app.extensions import db


class Resume(db.Model):
    __tablename__ = "resumes"
    __table_args__ = (
        db.CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_resumes_processing_status",
        ),
        db.Index("ix_resumes_user_created_at", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    content_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    extracted_text = db.Column(db.Text, nullable=True)
    sections = db.Column(db.JSON, nullable=True)
    skills = db.Column(db.JSON, nullable=True)
    processing_status = db.Column(db.String(20), nullable=False, server_default="pending")
    processing_error = db.Column(db.String(500), nullable=True)
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user = db.relationship("User", back_populates="resumes")
    analyses = db.relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")
