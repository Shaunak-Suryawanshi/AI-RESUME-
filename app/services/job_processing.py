"""Explainable first-pass processing for pasted job descriptions."""
from app.services.resume_processing import clean_resume_text, extract_skills


def process_job_description(description: str) -> dict:
    cleaned_description = clean_resume_text(description)
    return {
        "description": cleaned_description,
        "skills": extract_skills(cleaned_description),
    }
