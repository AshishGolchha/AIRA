from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.memory import memory_bp
from app.routes.profile import profile_bp

__all__ = ["auth_bp", "health_bp", "memory_bp", "profile_bp"]
