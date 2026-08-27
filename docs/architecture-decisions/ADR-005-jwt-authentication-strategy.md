# ADR-005: Stateless JWT Authentication Strategy

## Status
Accepted

## Context
AIRA is designed as a multi-user, API-driven investment research platform that will support web clients, mobile apps, and autonomous agent services. The system requires secure, scalable authentication that enforces strict user identity boundaries without introducing server-side session bottlenecks or tight coupling between the API server and stateful storage.

## Decision
Adopt stateless JSON Web Tokens (JWT) using `PyJWT` and native `werkzeug.security` password hashing:
1. **Password Security**: Passwords are never stored in plaintext. They are securely hashed using Werkzeug's established password hashing (`scrypt`/`pbkdf2`). Password hashes are strictly excluded from all API responses.
2. **Token Claims**: JWTs contain the minimal necessary claims: `sub` (user ID), `iat` (issued-at timestamp UTC), and `exp` (expiration timestamp UTC). No private user profile, investment preferences, or memory data is embedded in the token.
3. **Configurable Lifetime**: Token lifespan is managed via `JWT_ACCESS_TOKEN_EXPIRES_SECONDS` (default: 86400s / 24 hours), configurable through environment variables.
4. **Authentication Context**: Protected routes utilize the unified `@auth_required` decorator (`app/common/auth.py`), which validates token signatures, confirms user existence, and populates `flask.g.current_user`.

## Consequences
- **Positive**: Stateless, scalable authentication architecture with zero database session overhead.
- **Positive**: Consistent authentication context (`g.current_user`) guarantees centralized identity resolution across all protected routes.
- **Positive**: Minimal external dependencies (`PyJWT` + standard `werkzeug.security`).
- **Trade-off**: Token revocation requires short lifetimes or a future revocation blocklist if instant invalidation is needed.
