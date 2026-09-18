from sqlalchemy.sql import func

from app.extensions import db


class Analysis(db.Model):
    __tablename__ = "analyses"
    __table_args__ = (
        db.CheckConstraint("match_score >= 0 AND match_score <= 100", name="ck_analyses_match_score"),
        db.CheckConstraint(
            "ai_status IN ('not_requested', 'pending', 'completed', 'failed')",
            name="ck_analyses_ai_status",
        ),
        db.Index("ix_analyses_user_created_at", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    matching_skills = db.Column(db.JSON, nullable=False)
    missing_skills = db.Column(db.JSON, nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    ai_feedback = db.Column(db.JSON, nullable=True)
    ai_status = db.Column(db.String(20), nullable=False, server_default="not_requested")
    ai_error = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    user = db.relationship("User", back_populates="analyses")
    resume = db.relationship("Resume", back_populates="analyses")
    job = db.relationship("Job", back_populates="analyses")
