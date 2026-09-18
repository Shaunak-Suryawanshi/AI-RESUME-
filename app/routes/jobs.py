from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError

from app.extensions import db
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.services.auth import get_current_user, get_owned_or_404
from app.services.job_processing import process_job_description


jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/jobs")


def serialize_job(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "skills": job.skills,
        "processing_status": job.processing_status,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@jobs_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "No input data provided"}, 400
    try:
        job_data = JobCreate(**data)
    except ValidationError as error:
        return {"error": "Invalid input data", "details": error.errors()}, 400

    job = Job(**job_data.model_dump(), user_id=get_current_user().id)
    db.session.add(job)
    db.session.commit()
    return serialize_job(job), 201


@jobs_bp.route("", methods=["GET"])
@jwt_required()
def list_jobs():
    user = get_current_user()
    jobs = db.session.execute(
        db.select(Job).where(Job.user_id == user.id).order_by(Job.created_at.desc())
    ).scalars()
    return [serialize_job(job) for job in jobs], 200


@jobs_bp.route("/<int:job_id>", methods=["GET"])
@jwt_required()
def get_job(job_id: int):
    return serialize_job(get_owned_or_404(Job, job_id, get_current_user().id)), 200


@jobs_bp.route("/<int:job_id>", methods=["PATCH"])
@jwt_required()
def update_job(job_id: int):
    data = request.get_json(silent=True)
    if not data:
        return {"error": "No input data provided"}, 400
    try:
        update_data = JobUpdate(**data)
    except ValidationError as error:
        return {"error": "Invalid input data", "details": error.errors()}, 400

    job = get_owned_or_404(Job, job_id, get_current_user().id)
    changed_fields = update_data.model_dump(exclude_unset=True)
    for field, value in changed_fields.items():
        setattr(job, field, value)
    if "description" in changed_fields:
        job.skills = None
        job.processing_status = "pending"
    db.session.commit()
    return serialize_job(job), 200


@jobs_bp.route("/<int:job_id>/process", methods=["POST"])
@jwt_required()
def process_job(job_id: int):
    job = get_owned_or_404(Job, job_id, get_current_user().id)
    result = process_job_description(job.description)
    job.description = result["description"]
    job.skills = result["skills"]
    job.processing_status = "completed"
    db.session.commit()
    return serialize_job(job), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id: int):
    job = get_owned_or_404(Job, job_id, get_current_user().id)
    db.session.delete(job)
    db.session.commit()
    return "", 204
