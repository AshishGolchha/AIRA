# ADR-021: Production Security, Deployment & Operational Readiness

## Status
Accepted (Phase 18)

## Context
Following the completion of the foundational and integration phases (Phases 1–17), AIRA required comprehensive hardening across security boundaries, configuration safety, rate limiting, liveness/readiness health probes, browser-level end-to-end testing, and continuous integration.

## Architectural Decisions

### 1. Fail-Fast Production Configuration Validation
- **Problem**: Applications running in production can silently inherit weak development fallback secrets (e.g. `dev-secret-key-change-in-production`), risking token tampering and unauthorized access.
- **Decision**: Implemented `validate_production_config(config)` in `app/config.py`. In `FLASK_ENV=production`, the application validates at startup that `SECRET_KEY` and `JWT_SECRET_KEY` are distinct, cryptographically strong strings (> 32 chars), that `DEBUG` is disabled, and that a production relational database connection is configured. Failure to meet these requirements raises an explicit `RuntimeError`, aborting startup before serving traffic.

### 2. CORS Allowlist & Preflight Isolation
- **Problem**: Unrestricted CORS (`Access-Control-Allow-Origin: *`) exposes APIs to unauthorized cross-origin requests from arbitrary websites.
- **Decision**: Implemented dynamic origin matching in `app/__init__.py` against `CORS_ALLOWED_ORIGINS`. In production, only explicitly allowlisted web origins receive CORS access headers. `OPTIONS` preflight requests are handled cleanly with 200/204 status, caching directives (`Access-Control-Max-Age: 86400`), and authorized header lists (`Content-Type, Authorization, X-Request-ID`).

### 3. Defense-in-Depth Security Headers
- **Decision**: Enabled standard security headers globally on all API responses:
  - `X-Content-Type-Options: nosniff` (MIME sniffing prevention)
  - `X-Frame-Options: DENY` (Clickjacking defense)
  - `Referrer-Policy: strict-origin-when-cross-origin` (Privacy preservation)
  - `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()` (Browser API restriction)
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (HTTPS enforcement in production)
  - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none'; ...` (XSS & injection mitigation)

### 4. Sliding-Window Rate Limiting
- **Decision**: Built a thread-safe, in-memory sliding window rate limiter in `app/common/rate_limit.py`. Configured endpoint-specific thresholds on expensive / abuse-prone routes:
  - `/api/v1/auth/login`: 15 requests / min
  - `/api/v1/auth/register`: 10 requests / min
  - `/api/v1/research/analyze`: 10 requests / min
  - `/api/v1/portfolio/intelligence`: 10 requests / min
  - `/api/v1/alerts/check`: 30 requests / min
  - `/api/v1/notifications/endpoints`: 20 requests / min
  When rate limits are exceeded, requests return HTTP 429 Too Many Requests with standardized error JSON, `Retry-After`, and `X-RateLimit-*` telemetry headers.

### 5. Decoupled Liveness & Readiness Probes
- **Decision**:
  - `GET /api/v1/health` (and `/health/live`): **Liveness Probe** verifying Flask process uptime. Zero external calls.
  - `GET /api/v1/health/ready`: **Readiness Probe** verifying primary MySQL database responsiveness via a fast `SELECT 1` query. Returns 200 if connected, 503 if unreachable. Zero AI, vector, or external provider calls are executed.

### 6. End-to-End Browser Validation (Playwright)
- **Decision**: Integrated Playwright browser testing in `frontend/e2e/` to validate critical user flows (unauthenticated redirect, login, dashboard rendering, multi-page routing, session teardown) under headless Chromium.

### 7. Continuous Integration
- **Decision**: Configured automated GitHub Actions workflow (`.github/workflows/ci.yml`) to enforce backend pytest suites (180+ tests), frontend TypeScript typecheck, Vitest component test suites, production build, and Playwright E2E suites.

## Consequences
- **Positive**:
  - Elimination of insecure default credentials in production environments.
  - Granular abuse prevention on resource-intensive AI and authentication routes.
  - Zero-drift between backend and frontend contracts.
  - Complete automated CI pipeline with end-to-end browser verification.
