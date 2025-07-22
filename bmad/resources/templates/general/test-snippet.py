# Test Snippet (pytest)

def test_login_success(client):
    response = client.post("/auth/login", json={"email": "test@test.com", "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()
