import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def build_mysql_uri() -> str:
    """Constructs MySQL database URI from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT", "3306")
    db_name = os.getenv("MYSQL_DATABASE")

    if all([user, password is not None, host, port, db_name]):
        encoded_password = quote_plus(password)
        return f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{db_name}"

    raise RuntimeError(
        "MySQL database configuration missing. Please provide DATABASE_URL "
        "or MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, and MYSQL_PASSWORD."
    )


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Supabase (Persistent User Memory)
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    # Gemini AI & Embeddings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini/gemini-2.0-flash")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    MEMORY_SIMILARITY_THRESHOLD = float(os.getenv("MEMORY_SIMILARITY_THRESHOLD", "0.5"))

    # Authentication settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_SECONDS", "86400"))
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "")

    # Alert & Monitoring Configuration
    ALERT_PRICE_MOVE_THRESHOLD_PERCENT = float(os.getenv("ALERT_PRICE_MOVE_THRESHOLD_PERCENT", "5.0"))
    ALERT_PORTFOLIO_GAIN_LOSS_THRESHOLD_PERCENT = float(os.getenv("ALERT_PORTFOLIO_GAIN_LOSS_THRESHOLD_PERCENT", "10.0"))
    ALERT_MONITORING_ENABLED = os.getenv("ALERT_MONITORING_ENABLED", "true").lower() in ("true", "1")
    NOTIFICATION_ENABLED = os.getenv("NOTIFICATION_ENABLED", "true").lower() in ("true", "1")

    # External Notification Channels
    NOTIFICATION_EMAIL_ENABLED = os.getenv("NOTIFICATION_EMAIL_ENABLED", "false").lower() in ("true", "1")
    NOTIFICATION_EMAIL_PROVIDER = os.getenv("NOTIFICATION_EMAIL_PROVIDER", "resend")
    NOTIFICATION_EMAIL_API_KEY = os.getenv("NOTIFICATION_EMAIL_API_KEY", "")
    NOTIFICATION_EMAIL_FROM = os.getenv("NOTIFICATION_EMAIL_FROM", "alerts@aira.internal")
    NOTIFICATION_WEBHOOK_ENABLED = os.getenv("NOTIFICATION_WEBHOOK_ENABLED", "true").lower() in ("true", "1")
    NOTIFICATION_WEBHOOK_TIMEOUT_SECONDS = float(os.getenv("NOTIFICATION_WEBHOOK_TIMEOUT_SECONDS", "5.0"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = build_mysql_uri()


class ProductionConfig(BaseConfig):
    DEBUG = False

    def __init__(self):
        self.SQLALCHEMY_DATABASE_URI = build_mysql_uri()


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(config_name: str | None = None) -> BaseConfig:
    """Returns the appropriate config instance based on environment or name."""
    env = config_name or os.getenv("FLASK_ENV", "development").lower()
    config_class = CONFIG_MAP.get(env, DevelopmentConfig)
    return config_class()
