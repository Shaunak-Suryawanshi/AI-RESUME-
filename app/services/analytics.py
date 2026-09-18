"""Read-only SQLAlchemy queries for the authenticated user's dashboard."""
from sqlalchemy import case, func

from app.extensions import db
from app.models.analysis import Analysis
from app.models.job import Job


def get_analysis_dashboard(user_id: int) -> dict:
    """Return aggregate analysis statistics without loading all rows into Python."""
    completed_ai_count = func.coalesce(
        func.sum(case((Analysis.ai_status == "completed", 1), else_=0)), 0
    )
    summary_statement = db.select(
        func.count(Analysis.id).label("total_analyses"),
        func.coalesce(func.avg(Analysis.match_score), 0).label("average_match_score"),
        completed_ai_count.label("ai_completed_count"),
    ).where(Analysis.user_id == user_id)
    summary = db.session.execute(summary_statement).one()

    # Scalar subquery: calculate this user's maximum once, then use it to find
    # the best analysis without bringing every analysis row into Python.
    best_score_subquery = (
        db.select(func.max(Analysis.match_score))
        .where(Analysis.user_id == user_id)
        .scalar_subquery()
    )
    best_match_statement = (
        db.select(Analysis)
        .where(Analysis.user_id == user_id, Analysis.match_score == best_score_subquery)
        .order_by(Analysis.created_at.desc())
        .limit(1)
    )
    best_match = db.session.execute(best_match_statement).scalar_one_or_none()

    # JOIN + GROUP BY: one row per job, not one row per analysis.
    job_performance_statement = (
        db.select(
            Job.id,
            Job.title,
            Job.company,
            func.count(Analysis.id).label("analysis_count"),
            func.round(func.avg(Analysis.match_score), 2).label("average_match_score"),
        )
        .join(Analysis, Analysis.job_id == Job.id)
        .where(Analysis.user_id == user_id)
        .group_by(Job.id, Job.title, Job.company)
        .order_by(func.avg(Analysis.match_score).desc(), Job.id)
    )
    job_performance = [
        {
            "job_id": row.id,
            "title": row.title,
            "company": row.company,
            "analysis_count": row.analysis_count,
            "average_match_score": float(row.average_match_score),
        }
        for row in db.session.execute(job_performance_statement)
    ]

    return {
        "total_analyses": summary.total_analyses,
        "average_match_score": round(float(summary.average_match_score), 2),
        "ai_completed_count": int(summary.ai_completed_count),
        "best_match": (
            {
                "analysis_id": best_match.id,
                "resume_id": best_match.resume_id,
                "job_id": best_match.job_id,
                "match_score": best_match.match_score,
            }
            if best_match
            else None
        ),
        "job_performance": job_performance,
    }
