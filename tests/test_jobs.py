from tests.conftest import register_and_login


def _job_payload():
    return {
        "title": "Python Backend Developer",
        "company": "CareerLens",
        "location": "Pune",
        "description": "Build REST API services using Python, Flask, PostgreSQL, Docker, and Git.",
    }


def test_user_cannot_read_another_users_job(client, auth_headers):
    created = client.post("/api/jobs", json=_job_payload(), headers=auth_headers)
    assert created.status_code == 201

    other_headers = register_and_login(client, email="other@example.com")
    response = client.get(f"/api/jobs/{created.json['id']}", headers=other_headers)
    assert response.status_code == 404
