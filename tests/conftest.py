import pytest

from app import create_app
from app.extensions import db


@pytest.fixture()
def app(monkeypatch, tmp_path):
    """Create an isolated app, database, and upload folder for every test."""
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("UPLOAD_FOLDER", str(tmp_path / "uploads"))
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret-key-that-is-long-enough")
    monkeypatch.setenv("SECRET_KEY", "test-flask-secret-key-that-is-long-enough")
    application = create_app()
    application.config.update(TESTING=True)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_login(client, *, email="user@example.com", password="securepass123"):
    response = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": email, "password": password},
    )
    assert response.status_code == 201
    login = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json['access_token']}"}


@pytest.fixture()
def auth_headers(client):
    return register_and_login(client)
