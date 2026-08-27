import pytest
from app.common.auth import generate_token
from app.models.user import User


def test_registration_success(client):
    """Verify successful user registration with profile creation."""
    payload = {
        "email": "investor@example.com",
        "password": "SecurePassword123!",
        "display_name": "Pro Investor",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "Bearer"

    user = data["data"]["user"]
    assert user["email"] == "investor@example.com"
    assert user["profile"]["display_name"] == "Pro Investor"
    assert "password" not in user
    assert "password_hash" not in user


def test_registration_duplicate_email(client):
    """Verify registration with duplicate email returns 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    data = res2.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"


def test_registration_email_normalization(client):
    """Verify emails are normalized (trimmed and lowercased)."""
    res1 = client.post(
        "/api/v1/auth/register",
        json={"email": "  Normalized@Example.COM  ", "password": "Password123!"},
    )
    assert res1.status_code == 201
    assert res1.get_json()["data"]["user"]["email"] == "normalized@example.com"

    # Attempt registration with lowercased version should fail with 409
    res2 = client.post(
        "/api/v1/auth/register",
        json={"email": "normalized@example.com", "password": "Password123!"},
    )
    assert res2.status_code == 409


def test_registration_invalid_inputs(client):
    """Verify validation on registration inputs."""
    # Missing email
    res1 = client.post("/api/v1/auth/register", json={"password": "Password123!"})
    assert res1.status_code == 400

    # Missing password
    res2 = client.post("/api/v1/auth/register", json={"email": "user@example.com"})
    assert res2.status_code == 400

    # Invalid email format
    res3 = client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email", "password": "Password123!"},
    )
    assert res3.status_code == 400
    assert "Invalid email" in res3.get_json()["error"]["message"]

    # Short password (< 8 chars)
    res4 = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert res4.status_code == 400
    assert "at least 8 characters" in res4.get_json()["error"]["message"]


def test_password_hash_stored_in_db(app, client):
    """Verify password is stored as a secure hash in the database, never plaintext."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "secure_user@example.com", "password": "MySecretPassword123"},
    )

    with app.app_context():
        user = User.query.filter_by(email="secure_user@example.com").first()
        assert user is not None
        assert user.password_hash != "MySecretPassword123"
        assert len(user.password_hash) > 30
        assert user.check_password("MySecretPassword123") is True
        assert user.check_password("WrongPassword") is False


def test_login_success(client):
    """Verify login returns 200 and access token for valid credentials."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "login_user@example.com", "password": "ValidPassword123"},
    )

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "login_user@example.com", "password": "ValidPassword123"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["email"] == "login_user@example.com"


def test_login_normalized_email(client):
    """Verify login handles uppercase and whitespace email variations."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "case_test@example.com", "password": "ValidPassword123"},
    )

    res = client.post(
        "/api/v1/auth/login",
        json={"email": "  CASE_TEST@Example.com  ", "password": "ValidPassword123"},
    )
    assert res.status_code == 200


def test_login_invalid_credentials(client):
    """Verify invalid credentials return 401 with generic error message."""
    client.post(
        "/api/v1/auth/register",
        json={"email": "existing@example.com", "password": "ValidPassword123"},
    )

    # Wrong password
    res1 = client.post(
        "/api/v1/auth/login",
        json={"email": "existing@example.com", "password": "WrongPassword!"},
    )
    assert res1.status_code == 401
    assert res1.get_json()["error"]["message"] == "Invalid email or password."

    # Nonexistent email
    res2 = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "ValidPassword123"},
    )
    assert res2.status_code == 401
    assert res2.get_json()["error"]["message"] == "Invalid email or password."


def test_auth_me_success(client):
    """Verify /api/v1/auth/me returns current user data with valid token."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "me_user@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "me_user@example.com"


def test_auth_me_unauthorized_cases(app, client):
    """Verify unauthenticated, malformed, invalid, and expired tokens return 401."""
    # No header
    res1 = client.get("/api/v1/auth/me")
    assert res1.status_code == 401

    # Malformed header (missing 'Bearer ')
    res2 = client.get("/api/v1/auth/me", headers={"Authorization": "Basic abc123xyz"})
    assert res2.status_code == 401

    # Invalid token signature
    res3 = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert res3.status_code == 401

    # Expired token
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "expired_user@example.com", "password": "Password123!"},
    )
    user_id = reg.get_json()["data"]["user"]["id"]

    with app.app_context():
        expired_token = generate_token(user_id, expires_in_seconds=-10)

    res4 = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res4.status_code == 401
