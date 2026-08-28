# ADR-022: Production Containerization, Observability & Release Deployment

## Status
Accepted

## Context
Following the completion of core financial intelligence engines, multi-tenant isolation, notification retries, responsive React frontend, and Phase 18 security hardening, AIRA required a reproducible, production-deployable containerization strategy and operational readiness architecture.

Key operational requirements:
1. **Containerized Production Backend**: Eliminate the development Flask server in favor of a multi-threaded Gunicorn WSGI runtime executing on a hardened non-root container image.
2. **Optimized Frontend Serving**: Serve production-compiled Vite static assets via high-performance Nginx with gzip compression, SPA client-side fallback routing, immutable asset caching, and reverse proxying for `/api/` endpoints.
3. **Reproducible Local Production Stack**: Local orchestration with Docker Compose coordinating Frontend, Backend, and MySQL 8.0 with explicit service health checks and isolated networking.
4. **Deterministic Migration Lifecycle**: Safe Alembic migration execution (`RUN_MIGRATIONS=true`) during container startup without relying on destructive table creation.
5. **Observability & Request Tracing**: End-to-end `X-Request-ID` propagation, structured request logging with latency measurements, and strict secret redaction.
6. **Decoupled Health Semantics**: Process liveness (`/health/live`) with zero external load, database readiness (`/health/ready`) with zero AI provider cost, and canonical version metadata (`/version`).

## Decision

### 1. Backend Container Architecture
- **Base Image**: `python:3.10-slim` Debian-based minimal image.
- **Process Model**: Gunicorn WSGI server running with 2 worker processes and 4 threads per worker (`--worker-class gthread`), backed by `/dev/shm` temporary storage to prevent worker lockups.
- **Security Boundary**: Runs under an unprivileged user `aira` (UID 10001). No development packages, test suites, or `.env` secrets are copied into the container layers.
- **Entrypoint Strategy**: `docker/entrypoint.sh` inspects `RUN_MIGRATIONS` environment variable, conditionally executes `flask db upgrade`, and gracefully `exec`s the Gunicorn process for proper POSIX signal (SIGTERM/SIGINT) propagation.

### 2. Frontend Nginx Serving & Reverse Proxy
- **Multi-Stage Build**:
  - `Stage 1 (builder)`: Compiles React 18 / TypeScript bundle using Node 20.
  - `Stage 2 (production)`: Packages static assets into `nginx:1.27-alpine`.
- **SPA Routing**: `try_files $uri $uri/ /index.html;` ensures deep browser navigation across all application routes (`/app/dashboard`, `/app/portfolio`, `/app/research`, etc.) works seamlessly.
- **Reverse Proxy**: Internal Nginx routing for `/api/` traffic to `http://backend:5000` with header forwarding (`Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Request-ID`).

### 3. Orchestration & Local Topology
```text
Browser Client
     │
     ▼ (Port 8080)
┌─────────────────────────────────────────────────────────┐
│ Nginx Container (aira-frontend)                         │
│  ├── Serves SPA Static Files (/index.html, /assets/*)   │
│  └── Reverse Proxies /api/*                             │
└──────────────────────────┬──────────────────────────────┘
                           │ internal:5000
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Gunicorn WSGI Container (aira-backend)                  │
│  ├── Flask Application Factory                          │
│  ├── Request ID Tracing & Logging                       │
│  ├── Sliding-Window Rate Limiting                       │
│  └── Decoupled Liveness & Readiness Probes              │
└──────────────────────────┬──────────────────────────────┘
                           │ internal:3306
                           ▼
┌─────────────────────────────────────────────────────────┐
│ Relational Database (aira-mysql:8.0)                    │
│  ├── Named Persistent Volume (aira_mysql_data)          │
│  └── Healthcheck: mysqladmin ping                       │
└─────────────────────────────────────────────────────────┘
```

### 4. Canonical Versioning & Health Contracts
- `app/version.py`: Single source of truth defining `__version__ = "1.0.0"`.
- `GET /api/v1/version`: Returns service name, version, and UTC timestamp.
- `GET /api/v1/health` / `GET /api/v1/health/live`: Fast process liveness probe.
- `GET /api/v1/health/ready`: Primary database ping (`SELECT 1`).

## Consequences

### Positive
- Fully reproducible local production-like stack runnable with a single command: `docker compose up --build`.
- Zero CORS friction in production because browser traffic enters through the unified Nginx origin.
- Defense-in-depth security: non-root containers, no baked credentials, fail-fast configuration validation.
- Clean continuous integration pipeline verifying unit, integration, frontend, E2E, and Docker builds.

### Operational Considerations
- External providers (Google Gemini, Supabase Vector Memory) remain configurable via environment variables and are not containerized.
- In-memory rate limiting and monitoring locks operate safely within the container boundary; high-scale horizontal multi-replica deployments can bind to Redis in future phases if needed.
