from app.extensions import db
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User


def test_analysis_calculates_explainable_skill_overlap(app, client, auth_headers):
    with app.app_context():
        user = db.session.execute(db.select(User).where(User.email == "user@example.com")).scalar_one()
        resume = Resume(
            original_filename="resume.pdf", stored_filename="matching-resume.pdf",
            content_type="application/pdf", file_size=1, user_id=user.id,
            skills=["Python", "Flask", "Docker"], processing_status="completed",
        )
        job = Job(
            title="Backend Developer", company="CareerLens",
            description="Build Python services with Flask, Docker, PostgreSQL, and Git.",
            user_id=user.id, skills=["Python", "Flask", "Docker", "PostgreSQL", "Git"],
            processing_status="completed",
        )
        db.session.add_all([resume, job])
        db.session.commit()
        resume_id, job_id = resume.id, job.id

    response = client.post(
        "/api/analyses",
        json={"resume_id": resume_id, "job_id": job_id, "include_ai": False},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json["match_score"] == 60.0
    assert response.json["matching_skills"] == ["Python", "Flask", "Docker"]
    assert response.json["missing_skills"] == ["PostgreSQL", "Git"]
