import pytest
from app.config import DevelopmentConfig, ProductionConfig, TestingConfig, build_mysql_uri, get_config


def test_testing_config():
    """Verify testing configuration uses isolated in-memory SQLite."""
    config = TestingConfig()
    assert config.TESTING is True
    assert config.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False


def test_mysql_uri_from_database_url(monkeypatch):
    """Verify DATABASE_URL takes precedence when provided."""
    expected_uri = "mysql+pymysql://custom_user:custom_pass@dbhost:3306/custom_db"
    monkeypatch.setenv("DATABASE_URL", expected_uri)

    uri = build_mysql_uri()
    assert uri == expected_uri


def test_mysql_uri_from_components(monkeypatch):
    """Verify MySQL URI is properly constructed from individual environment components."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MYSQL_USER", "aira_admin")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret#pass")
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_DATABASE", "aira_production")

    uri = build_mysql_uri()
    assert uri == "mysql+pymysql://aira_admin:secret%23pass@127.0.0.1:3307/aira_production"


def test_mysql_missing_config_fails(monkeypatch):
    """Verify lack of MySQL configuration raises an explicit RuntimeError (no silent fallback)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MYSQL_USER", raising=False)
    monkeypatch.delenv("MYSQL_PASSWORD", raising=False)
    monkeypatch.delenv("MYSQL_HOST", raising=False)
    monkeypatch.delenv("MYSQL_DATABASE", raising=False)

    with pytest.raises(RuntimeError, match="MySQL database configuration missing"):
        build_mysql_uri()


def test_get_config_mapping(monkeypatch):
    """Verify get_config resolves correct configuration class."""
    test_cfg = get_config("testing")
    assert isinstance(test_cfg, TestingConfig)
    assert test_cfg.TESTING is True
