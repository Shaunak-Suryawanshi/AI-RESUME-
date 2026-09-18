def test_me_requires_a_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401
    assert response.json["error"] == "Authentication required"


def test_registered_user_can_get_current_profile(client, auth_headers):
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == "user@example.com"
    assert "password_hash" not in response.json
