from app.routes.alerts import alerts_bp
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.health import health_bp
from app.routes.memory import memory_bp
from app.routes.monitoring import monitoring_bp
from app.routes.notifications import notifications_bp
from app.routes.portfolio import portfolio_bp
from app.routes.profile import profile_bp
from app.routes.research import research_bp
from app.routes.watchlist import watchlist_bp

__all__ = [
    "alerts_bp",
    "auth_bp",
    "dashboard_bp",
    "health_bp",
    "memory_bp",
    "monitoring_bp",
    "notifications_bp",
    "portfolio_bp",
    "profile_bp",
    "research_bp",
    "watchlist_bp",
]
