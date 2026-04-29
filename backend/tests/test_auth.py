"""Tests for authentication endpoints."""


class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "password" not in data

    def test_register_duplicate_username(self, client, test_user):
        resp = client.post("/api/auth/register", json={
            "username": test_user["username"],
            "email": "different@example.com",
            "password": "anotherpass",
        })
        assert resp.status_code == 400

    def test_login_success(self, client, test_user):
        resp = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": test_user["password"],
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, test_user):
        resp = client.post("/api/auth/login", json={
            "username": test_user["username"],
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "noone",
            "password": "pass",
        })
        assert resp.status_code == 401

    def test_get_current_user(self, authorized_client):
        resp = authorized_client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_unauthenticated_access(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_search_users(self, authorized_client):
        # Create a second user to search for
        client.post("/api/auth/register", json={
            "username": "searchable",
            "email": "search@example.com",
            "password": "pass123",
        })
        resp = authorized_client.get("/api/auth/search?keyword=searchable")
        assert resp.status_code == 200
        usernames = [u["username"] for u in resp.json()]
        assert "searchable" in usernames
