import pytest
from app.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
    build_database_uri,
    build_mysql_uri,
    get_config,
)


def test_testing_config():
    """Verify testing configuration uses isolated in-memory SQLite."""
    config = TestingConfig()
    assert config.TESTING is True
    assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False


def test_database_uri_from_database_url(monkeypatch):
    """Verify DATABASE_URL takes precedence when provided."""
    expected_uri = "postgresql+psycopg2://custom_user:custom_pass@dbhost:5432/postgres"
    monkeypatch.setenv("DATABASE_URL", expected_uri)

    uri = build_database_uri()
    assert uri == expected_uri


def test_database_uri_converts_postgres_scheme(monkeypatch):
    """Verify postgres:// is converted to postgresql+psycopg2:// dialect."""
    raw_uri = "postgres://postgres:pass@db.project.supabase.co:5432/postgres"
    monkeypatch.setenv("DATABASE_URL", raw_uri)

    uri = build_database_uri()
    assert uri == "postgresql+psycopg2://postgres:pass@db.project.supabase.co:5432/postgres"


def test_database_uri_from_components(monkeypatch):
    """Verify PostgreSQL URI is properly constructed from individual environment components."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("PGUSER", "aira_admin")
    monkeypatch.setenv("PGPASSWORD", "secret#pass")
    monkeypatch.setenv("PGHOST", "127.0.0.1")
    monkeypatch.setenv("PGPORT", "5432")
    monkeypatch.setenv("PGDATABASE", "postgres")

    uri = build_database_uri()
    assert uri == "postgresql+psycopg2://aira_admin:secret%23pass@127.0.0.1:5432/postgres"


def test_database_missing_config_fails(monkeypatch):
    """Verify lack of database configuration raises an explicit RuntimeError (no silent fallback)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PGUSER", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("PGHOST", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("PGDATABASE", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_DATABASE", raising=False)

    with pytest.raises(RuntimeError, match="Database configuration missing"):
        build_database_uri()


def test_get_config_mapping(monkeypatch):
    """Verify get_config resolves correct configuration class."""
    test_cfg = get_config("testing")
    assert isinstance(test_cfg, TestingConfig)
    assert test_cfg.TESTING is True
