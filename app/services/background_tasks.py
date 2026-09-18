"""Small in-process background runner for development and portfolio demos.

It intentionally has no Redis/broker dependency. Tasks are not durable: an
application restart loses queued work, so production should use a proper queue.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask

from app.extensions import db
from app.models.resume import Resume
from app.services.resume_processing import ResumeProcessingError, process_resume_file


_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="careerlens-worker")


def submit_resume_processing(app: Flask, resume_id: int, user_id: int) -> None:
    """Queue the task and return immediately to the HTTP request."""
    _executor.submit(process_resume_task, app, resume_id, user_id)


def process_resume_task(app: Flask, resume_id: int, user_id: int) -> None:
    """Run PDF work in an application context, then persist the result."""
    with app.app_context():
        resume = db.session.get(Resume, resume_id)
        if resume is None or resume.user_id != user_id:
            return
        try:
            result = process_resume_file(
                Path(app.config["UPLOAD_FOLDER"]) / resume.stored_filename
            )
            resume.extracted_text = result["extracted_text"]
            resume.sections = result["sections"]
            resume.skills = result["skills"]
            resume.processing_status = "completed"
            resume.processing_error = None
            resume.processed_at = datetime.now(timezone.utc)
        except ResumeProcessingError as error:
            resume.processing_status = "failed"
            resume.processing_error = str(error)
            resume.processed_at = datetime.now(timezone.utc)
        except Exception:
            app.logger.exception("Unexpected resume processing failure for resume_id=%s", resume_id)
            resume.processing_status = "failed"
            resume.processing_error = "Unexpected processing failure"
            resume.processed_at = datetime.now(timezone.utc)
        finally:
            db.session.commit()
