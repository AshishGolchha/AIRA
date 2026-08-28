"""
AIRA Phase 19 Integration & Deployment Verification Tests
Validates container configurations, version metadata, logging, health probes,
and production-like API workflows.
"""

import os
from pathlib import Path
import pytest
from app import create_app
from app.config import BaseConfig, ProductionConfig, validate_production_config
from app.version import __version__, __service__


def test_version_endpoint_metadata(client):
    """Verify that /api/v1/version returns canonical service and version metadata."""
    res = client.get("/api/v1/version")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["service"] == __service__
    assert data["version"] == __version__
    assert "timestamp" in data


def test_liveness_and_readiness_contracts(client):
    """Verify that liveness and readiness probes conform to production specifications."""
    # Liveness (fast, zero dependency)
    res_live = client.get("/api/v1/health/live")
    assert res_live.status_code == 200
    assert res_live.get_json()["status"] == "ok"

    # Readiness (checks DB connectivity)
    res_ready = client.get("/api/v1/health/ready")
    assert res_ready.status_code == 200
    ready_data = res_ready.get_json()
    assert ready_data["status"] == "ready"
    assert ready_data["database"] == "connected"


def test_production_config_validation_rules():
    """Verify that production validation rejects insecure settings with clear explanations."""
    class BadKeyConfig(BaseConfig):
        SECRET_KEY = "too-short"
        JWT_SECRET_KEY = "also-too-short"
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@localhost/db"
        DEBUG = False

    with pytest.raises(RuntimeError) as exc_info:
        validate_production_config(BadKeyConfig())
    assert "SECRET_KEY" in str(exc_info.value)

    class SqliteProdConfig(BaseConfig):
        SECRET_KEY = "a" * 32
        JWT_SECRET_KEY = "b" * 32
        SQLALCHEMY_DATABASE_URI = "sqlite:///prod.db"
        DEBUG = False

    with pytest.raises(RuntimeError) as exc_info:
        validate_production_config(SqliteProdConfig())
    assert "relational database" in str(exc_info.value).lower()

    class DebugProdConfig(BaseConfig):
        SECRET_KEY = "a" * 32
        JWT_SECRET_KEY = "b" * 32
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@localhost/db"
        DEBUG = True

    with pytest.raises(RuntimeError) as exc_info:
        validate_production_config(DebugProdConfig())
    assert "DEBUG" in str(exc_info.value)


def test_valid_production_config_passes():
    """Verify that a compliant production config passes validation."""
    class ValidProdConfig(BaseConfig):
        SECRET_KEY = "x" * 48
        JWT_SECRET_KEY = "y" * 48
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://aira_user:pass@db:3306/aira_db"
        DEBUG = False

    errors = validate_production_config(ValidProdConfig())
    assert errors == []


def test_dockerfile_and_compose_structural_invariants():
    """Verify that container and orchestration files exist and adhere to production invariants."""
    root_dir = Path(__file__).resolve().parent.parent.parent

    # 1. Root Dockerfile
    dockerfile = (root_dir / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.10-slim" in dockerfile
    assert "USER aira" in dockerfile
    assert "EXPOSE 5000" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "gunicorn" in dockerfile
    assert "entrypoint.sh" in dockerfile

    # 2. Frontend Dockerfile
    frontend_dockerfile = (root_dir / "frontend" / "Dockerfile").read_text(encoding="utf-8")
    assert "node:20-alpine" in frontend_dockerfile
    assert "nginx:1.27-alpine" in frontend_dockerfile
    assert "EXPOSE 80" in frontend_dockerfile
    assert "HEALTHCHECK" in frontend_dockerfile

    # 3. Frontend Nginx Configuration
    nginx_conf = (root_dir / "frontend" / "nginx.conf").read_text(encoding="utf-8")
    assert "location /api/" in nginx_conf
    assert "proxy_pass http://backend:5000" in nginx_conf
    assert "try_files $uri $uri/ /index.html" in nginx_conf
    assert "gzip on" in nginx_conf

    # 4. Docker Compose
    compose_yaml = (root_dir / "docker-compose.yml").read_text(encoding="utf-8")
    assert "mysql:" in compose_yaml
    assert "backend:" in compose_yaml
    assert "frontend:" in compose_yaml
    assert "mysql_data:" in compose_yaml
    assert "aira-network" in compose_yaml
    assert "condition: service_healthy" in compose_yaml


def test_production_smoke_api_flow(client):
    """
    Executes a complete, deterministic smoke flow across core API surfaces
    verifying auth, profile, dashboard read-only contract, and request ID propagation.
    """
    # 1. Register a test investor
    reg_payload = {
        "email": "smoke.investor@aira.internal",
        "password": "SecurePassword123!",
        "display_name": "Smoke Test Investor",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    auth_data = reg_res.get_json()["data"]
    token = auth_data["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Request-ID": "smoke-test-trace-001",
    }

    # 2. Verify Profile
    prof_res = client.get("/api/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.headers.get("X-Request-ID") == "smoke-test-trace-001"
    assert prof_res.get_json()["data"]["profile"]["display_name"] == "Smoke Test Investor"

    # 3. Verify Dashboard Read-Only Contract
    dash_res = client.get("/api/v1/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.get_json()["data"]
    assert "portfolio" in dash_data
    assert "watchlist" in dash_data
    assert "alerts" in dash_data
    assert "monitoring" in dash_data

    # 4. Verify Unauthenticated Request is Rejected with Clean JSON
    unauth_res = client.get("/api/v1/dashboard")
    assert unauth_res.status_code == 401
    assert unauth_res.get_json()["success"] is False
    assert unauth_res.get_json()["error"]["code"] == "UNAUTHORIZED"
