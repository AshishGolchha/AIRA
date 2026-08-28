import time
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from flask import json
from app import create_app
from app.common.auth import generate_token
from app.common.rate_limit import _global_limiter
from app.config import BaseConfig, ProductionConfig, validate_production_config


def test_liveness_endpoint(client):
    """Verify that liveness probe returns 200 OK without invoking external dependencies."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "AIRA"
    assert data["version"] == "0.1.0"

    res_live = client.get("/api/v1/health/live")
    assert res_live.status_code == 200
    assert res_live.get_json()["status"] == "ok"


def test_readiness_endpoint_success(client):
    """Verify that readiness probe returns 200 when database connection is active."""
    res = client.get("/api/v1/health/ready")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_cors_headers_development_and_preflight(client):
    """Verify CORS preflight OPTIONS and origin reflection in development/testing."""
    # Preflight request
    res_opts = client.open(
        "/api/v1/health",
        method="OPTIONS",
        headers={"Origin": "http://localhost:5173"},
    )
    assert res_opts.status_code == 200
    assert res_opts.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"
    assert "GET" in res_opts.headers.get("Access-Control-Allow-Methods", "")
    assert "Authorization" in res_opts.headers.get("Access-Control-Allow-Headers", "")

    # Regular GET request
    res_get = client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert res_get.status_code == 200
    assert res_get.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"


def test_cors_allowed_and_disallowed_origins(monkeypatch):
    """Verify CORS strictly permits allowlisted origins and rejects untrusted origins."""
    app = create_app("testing")
    app.config["CORS_ALLOWED_ORIGINS"] = "https://app.aira.internal,https://admin.aira.internal"
    app.config["DEBUG"] = False
    app.config["TESTING"] = False

    with app.test_client() as c:
        # Allowed origin 1
        res_allowed = c.get("/api/v1/health", headers={"Origin": "https://app.aira.internal"})
        assert res_allowed.headers.get("Access-Control-Allow-Origin") == "https://app.aira.internal"

        # Disallowed origin
        res_blocked = c.get("/api/v1/health", headers={"Origin": "https://malicious-site.com"})
        assert res_blocked.headers.get("Access-Control-Allow-Origin") is None


def test_security_headers_present(client):
    """Verify all defense-in-depth HTTP security headers are populated."""
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in res.headers.get("Permissions-Policy", "")
    assert "frame-ancestors 'none'" in res.headers.get("Content-Security-Policy", "")


def test_request_id_tracing_and_preservation(client):
    """Verify X-Request-ID preservation and generation."""
    # 1. Custom incoming request ID preserved
    custom_id = "test-custom-trace-uuid-12345"
    res_custom = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert res_custom.headers.get("X-Request-ID") == custom_id

    # 2. Automatically generated request ID when omitted
    res_auto = client.get("/api/v1/health")
    assert res_auto.headers.get("X-Request-ID") is not None
    assert len(res_auto.headers.get("X-Request-ID")) > 10

    # 3. Error response contains request_id
    res_err = client.get("/api/v1/auth/me")
    assert res_err.status_code == 401
    data = res_err.get_json()
    assert "request_id" in data
    assert data["request_id"] == res_err.headers.get("X-Request-ID")


def test_jwt_security_and_expiry_validation(client):
    """Verify rejection of expired, unsigned, or malformed JWT tokens."""
    # 1. Missing token
    res_missing = client.get("/api/v1/auth/me")
    assert res_missing.status_code == 401
    assert res_missing.get_json()["error"]["code"] == "UNAUTHORIZED"

    # 2. Malformed token
    res_malformed = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert res_malformed.status_code == 401

    # 3. Expired token
    app = client.application
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "1",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload,
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    res_expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res_expired.status_code == 401

    # 4. None algorithm / unsigned token attack
    unsigned_payload = {
        "sub": "1",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    none_token = jwt.encode(
        unsigned_payload,
        "a-very-long-dummy-wrong-secret-key-32-chars-long",
        algorithm="HS256",
    )
    res_unsigned = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {none_token}"},
    )
    assert res_unsigned.status_code == 401


def test_rate_limiting_enforcement_and_headers(client):
    """Verify sliding window rate limiting returns 429 when threshold is exceeded."""
    _global_limiter.reset()
    client.application.config["RATELIMIT_ENABLED"] = True

    # Register test user
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "ratelimit_user@example.com", "password": "Password123!"},
    )
    assert reg.status_code == 201
    token = reg.get_json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Route /alerts/check is limited to 30 requests / min
    key = "alerts.check:user:1"
    _global_limiter.reset(key)

    # Execute 30 calls successfully
    for _ in range(30):
        r = client.post("/api/v1/alerts/check", headers=headers)
        assert r.status_code == 200

    # The 31st call should trigger 429 Too Many Requests
    r_blocked = client.post("/api/v1/alerts/check", headers=headers)
    assert r_blocked.status_code == 429
    data = r_blocked.get_json()
    assert data["error"]["code"] == "RATE_LIMITED"
    assert "Retry-After" in r_blocked.headers
    assert r_blocked.headers.get("X-RateLimit-Remaining") == "0"

    # Reset RATELIMIT_ENABLED to False for remaining test isolation
    client.application.config["RATELIMIT_ENABLED"] = False


def test_production_config_validation():
    """Verify that ProductionConfig validates secrets and rejects unsafe defaults."""
    # Test 1: Weak/default SECRET_KEY fails
    class DummyInsecureConfig(BaseConfig):
        SECRET_KEY = "dev-secret-key-change-in-production"
        JWT_SECRET_KEY = "a-very-long-and-secure-jwt-secret-key-for-prod-32-chars"
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://u:p@localhost:3306/db"
        DEBUG = False

    with pytest.raises(RuntimeError) as excinfo:
        validate_production_config(DummyInsecureConfig())
    assert "SECRET_KEY" in str(excinfo.value)

    # Test 2: Weak JWT_SECRET_KEY fails
    class DummyInsecureJWTConfig(BaseConfig):
        SECRET_KEY = "a-very-long-and-secure-secret-key-for-production-32-chars"
        JWT_SECRET_KEY = "short"
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://u:p@localhost:3306/db"
        DEBUG = False

    with pytest.raises(RuntimeError) as excinfo:
        validate_production_config(DummyInsecureJWTConfig())
    assert "JWT_SECRET_KEY" in str(excinfo.value)

    # Test 3: SQLite in production fails
    class DummySQLiteProdConfig(BaseConfig):
        SECRET_KEY = "a-very-long-and-secure-secret-key-for-production-32-chars"
        JWT_SECRET_KEY = "a-very-long-and-secure-jwt-secret-key-for-prod-32-chars"
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"
        DEBUG = False

    with pytest.raises(RuntimeError) as excinfo:
        validate_production_config(DummySQLiteProdConfig())
    assert "relational database" in str(excinfo.value)

    # Test 4: Fully valid production config passes
    class ValidProdConfig(BaseConfig):
        SECRET_KEY = "a-very-long-and-secure-secret-key-for-production-32-chars"
        JWT_SECRET_KEY = "a-very-long-and-secure-jwt-secret-key-for-prod-32-chars"
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@rds.amazonaws.com:3306/aira"
        DEBUG = False

    errors = validate_production_config(ValidProdConfig())
    assert len(errors) == 0
