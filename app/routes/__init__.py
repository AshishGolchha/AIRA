from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.memory import memory_bp
from app.routes.portfolio import portfolio_bp
from app.routes.profile import profile_bp
from app.routes.research import research_bp
from app.routes.watchlist import watchlist_bp

__all__ = [
    "auth_bp",
    "health_bp",
    "memory_bp",
    "portfolio_bp",
    "profile_bp",
    "research_bp",
    "watchlist_bp",
]
