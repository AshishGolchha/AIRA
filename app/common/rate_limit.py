import math
import threading
import time
from functools import wraps
from typing import Callable
from flask import current_app, g, jsonify, request


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(self):
        self._lock = threading.Lock()
        self._buckets: dict[str, list[float]] = {}

    def is_allowed(
        self, key: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int, int]:
        """
        Determines if a request for the given key is allowed.
        Returns:
            (allowed: bool, remaining: int, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._buckets.get(key, [])
            # Evict timestamps older than the sliding window
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= limit:
                oldest = valid_timestamps[0]
                retry_after = max(1, math.ceil(oldest + window_seconds - now))
                self._buckets[key] = valid_timestamps
                return False, 0, retry_after

            valid_timestamps.append(now)
            self._buckets[key] = valid_timestamps
            remaining = max(0, limit - len(valid_timestamps))
            return True, remaining, 0

    def reset(self, key: str | None = None) -> None:
        """Clears rate limit buckets for testing or maintenance."""
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()


# Global in-memory rate limiter instance
_global_limiter = SlidingWindowRateLimiter()


def get_client_identifier() -> str:
    """Derives client identifier from authenticated user ID or remote IP."""
    if hasattr(g, "current_user") and g.current_user:
        return f"user:{g.current_user.id}"
    # Honor X-Forwarded-For if available
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def rate_limit(
    limit: int,
    window_seconds: int = 60,
    key_func: Callable[[], str] | None = None,
):
    """
    Decorator to apply sliding-window rate limiting to Flask routes.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if rate limiting is enabled in current app config
            if not current_app.config.get("RATELIMIT_ENABLED", True):
                return f(*args, **kwargs)

            identifier = key_func() if key_func else get_client_identifier()
            bucket_key = f"{request.endpoint or request.path}:{identifier}"

            allowed, remaining, retry_after = _global_limiter.is_allowed(
                bucket_key, limit=limit, window_seconds=window_seconds
            )

            if not allowed:
                req_id = getattr(g, "request_id", "")
                response = jsonify({
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    },
                    "request_id": req_id,
                })
                response.status_code = 429
                response.headers["Retry-After"] = str(retry_after)
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = "0"
                return response

            response = f(*args, **kwargs)

            # If response is a Flask Response/tuple, append rate limit headers
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)

            return response

        return decorated_function

    return decorator
