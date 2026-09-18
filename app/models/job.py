from sqlalchemy.sql import func

from app.extensions import db


class Job(db.Model):
    __tablename__ = "jobs"
    __table_args__ = (
        db.CheckConstraint(
            "processing_status IN ('pending', 'completed', 'failed')",
            name="ck_jobs_processing_status",
        ),
        db.Index("ix_jobs_user_created_at", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.JSON, nullable=True)
    processing_status = db.Column(db.String(20), nullable=False, server_default="pending")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    user = db.relationship("User", back_populates="jobs")
    analyses = db.relationship("Analysis", back_populates="job", cascade="all, delete-orphan")
