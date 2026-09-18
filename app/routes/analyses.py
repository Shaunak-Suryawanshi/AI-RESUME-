from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import db
from app.models.analysis import Analysis
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.analysis import AnalysisCreate
from app.services.auth import get_current_user, get_owned_or_404
from app.services.llm import LLMServiceError, generate_json
from app.services.matching import build_feedback_prompt, calculate_skill_match
from app.services.analytics import get_analysis_dashboard
from app.services.cache import dashboard_cache, dashboard_cache_key


analyses_bp = Blueprint("analyses", __name__, url_prefix="/api/analyses")


def serialize_analysis(analysis: Analysis) -> dict:
    return {
        "id": analysis.id,
        "resume_id": analysis.resume_id,
        "job_id": analysis.job_id,
        "matching_skills": analysis.matching_skills,
        "missing_skills": analysis.missing_skills,
        "match_score": analysis.match_score,
        "ai_status": analysis.ai_status,
        "ai_feedback": analysis.ai_feedback,
        "ai_error": analysis.ai_error,
        "created_at": analysis.created_at.isoformat(),
    }


@analyses_bp.route("", methods=["POST"])
@jwt_required()
def create_analysis():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "No input data provided"}, 400
    try:
        analysis_data = AnalysisCreate(**data)
    except ValidationError as error:
        return {"error": "Invalid input data", "details": error.errors()}, 400

    user = get_current_user()
    resume = get_owned_or_404(Resume, analysis_data.resume_id, user.id)
    job = get_owned_or_404(Job, analysis_data.job_id, user.id)
    if resume.processing_status != "completed":
        return {"error": "Resume must be processed before analysis"}, 409
    if job.processing_status != "completed":
        return {"error": "Job must be processed before analysis"}, 409

    match = calculate_skill_match(resume.skills, job.skills)
    analysis = Analysis(
        **match,
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id,
        ai_status="pending" if analysis_data.include_ai else "not_requested",
    )

    if analysis_data.include_ai:
        system_prompt, user_content = build_feedback_prompt(
            resume_skills=resume.skills or [],
            job_title=job.title,
            company=job.company,
            job_skills=job.skills or [],
            matching_skills=match["matching_skills"],
            missing_skills=match["missing_skills"],
        )
        try:
            analysis.ai_feedback = generate_json(
                system_prompt=system_prompt, user_content=user_content
            )
            analysis.ai_status = "completed"
        except LLMServiceError as error:
            # Preserve the deterministic analysis even if the optional provider fails.
            analysis.ai_status = "failed"
            analysis.ai_error = str(error)

    db.session.add(analysis)
    db.session.commit()
    dashboard_cache.invalidate(dashboard_cache_key(user.id))
    return serialize_analysis(analysis), 201


@analyses_bp.route("", methods=["GET"])
@jwt_required()
def list_analyses():
    user = get_current_user()
    analyses = db.session.execute(
        db.select(Analysis).where(Analysis.user_id == user.id).order_by(Analysis.created_at.desc())
    ).scalars()
    return [serialize_analysis(analysis) for analysis in analyses], 200


@analyses_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_analysis_stats():
    """Aggregate dashboard data with database-side SQL, scoped to the owner."""
    user_id = get_current_user().id
    dashboard = dashboard_cache.get_or_set(
        dashboard_cache_key(user_id),
        current_app.config["DASHBOARD_CACHE_TTL_SECONDS"],
        lambda: get_analysis_dashboard(user_id),
    )
    return dashboard, 200


@analyses_bp.route("/<int:analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis(analysis_id: int):
    return serialize_analysis(get_owned_or_404(Analysis, analysis_id, get_current_user().id)), 200
