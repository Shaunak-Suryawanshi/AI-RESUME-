from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.resume import Resume
from app.services.auth import get_current_user, get_owned_or_404
from app.services.resume_storage import delete_resume_file, save_resume_file, validate_resume_file
from app.services.background_tasks import submit_resume_processing


resumes_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")


def serialize_resume(resume: Resume) -> dict:
    return {
        "id": resume.id,
        "original_filename": resume.original_filename,
        "content_type": resume.content_type,
        "file_size": resume.file_size,
        "created_at": resume.created_at.isoformat(),
        "processing_status": resume.processing_status,
        "processing_error": resume.processing_error,
        "processed_at": resume.processed_at.isoformat() if resume.processed_at else None,
        "sections": resume.sections,
        "skills": resume.skills,
    }


@resumes_bp.route("", methods=["POST"])
@jwt_required()
def upload_resume():
    upload = request.files.get("file")
    validation_error = validate_resume_file(upload)
    if validation_error:
        return {"error": validation_error}, 400

    original_filename, stored_filename, file_size = save_resume_file(
        upload, current_app.config["UPLOAD_FOLDER"]
    )
    resume = Resume(
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type="application/pdf",
        file_size=file_size,
        user_id=get_current_user().id,
    )
    try:
        db.session.add(resume)
        db.session.commit()
    except Exception:
        db.session.rollback()
        delete_resume_file(current_app.config["UPLOAD_FOLDER"], stored_filename)
        raise
    return serialize_resume(resume), 201


@resumes_bp.route("", methods=["GET"])
@jwt_required()
def list_resumes():
    user = get_current_user()
    resumes = db.session.execute(
        db.select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    ).scalars()
    return [serialize_resume(resume) for resume in resumes], 200


@resumes_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id: int):
    user = get_current_user()
    return serialize_resume(get_owned_or_404(Resume, resume_id, user.id)), 200


@resumes_bp.route("/<int:resume_id>/process", methods=["POST"])
@jwt_required()
def process_resume(resume_id: int):
    """Queue PDF processing and let the client poll its processing status."""
    user = get_current_user()
    resume = get_owned_or_404(Resume, resume_id, user.id)
    if resume.processing_status == "processing":
        return {"error": "Resume processing is already running"}, 409

    resume.processing_status = "processing"
    resume.processing_error = None
    db.session.commit()
    submit_resume_processing(current_app._get_current_object(), resume.id, user.id)
    return serialize_resume(resume), 202


@resumes_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id: int):
    user = get_current_user()
    resume = get_owned_or_404(Resume, resume_id, user.id)
    delete_resume_file(current_app.config["UPLOAD_FOLDER"], resume.stored_filename)
    db.session.delete(resume)
    db.session.commit()
    return "", 204
