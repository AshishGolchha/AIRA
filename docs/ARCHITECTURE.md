# AIRA Architecture

**AIRA — Autonomous Investment Research & Analysis**

This document is the single authoritative architecture reference for the AIRA platform. It describes the final, production-ready system as it stands today. For a new developer joining the project, this document explains how AIRA is built, why key decisions were made, and how the components fit together.

---

## 1. System Overview

AIRA is a multi-user, multi-tenant AI-powered investment research and portfolio intelligence platform. It combines:

- **Autonomous AI research** — multi-agent CrewAI pipelines backed by Google Gemini produce verifiable, evidence-grounded equity research reports.
- **Deterministic financial analytics** — portfolio valuation, watchlist monitoring, and alert detection use pure Python arithmetic and SQL rules — no LLM involvement in numerical calculations.
- **Persistent semantic memory** — per-user investment preferences and strategy notes are embedded via Gemini and stored in `pgvector` for personalized research context.
- **Automated alert monitoring** — scheduled batch runs detect portfolio and watchlist price movements and route notifications to configurable channels.
- **A modern React frontend** — a TypeScript/Vite SPA provides the full authenticated dashboard, research workspace, portfolio management, and public landing page.

The platform is designed for Indian retail investors and financial professionals, with native INR currency handling throughout the UI and conversion layer.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| **Backend framework** | Flask (Application Factory pattern) |
| **WSGI server (production)** | Gunicorn (`gthread` worker class, 2 workers × 4 threads) |
| **Primary database** | Supabase PostgreSQL (single authoritative database) |
| **ORM** | SQLAlchemy + `psycopg2-binary` |
| **Schema migrations** | Flask-Migrate (Alembic) |
| **Vector memory** | `pgvector` extension on Supabase PostgreSQL |
| **AI embeddings** | Google Gemini `text-embedding-004` (768 dimensions) |
| **AI research agents** | CrewAI + Google Gemini `gemini-2.0-flash` |
| **Financial data** | `yfinance` (via `FinancialDataService` abstraction) |
| **Authentication** | Stateless JWT (`PyJWT` + `werkzeug.security`) |
| **Frontend framework** | React 18 + TypeScript + Vite |
| **Frontend styling** | Tailwind CSS with custom financial theme extensions |
| **Frontend routing** | React Router v6 |
| **Frontend serving (production)** | Nginx (multi-stage Docker build, SPA fallback routing) |
| **Containerization** | Docker + Docker Compose |
| **CI** | GitHub Actions |

---

## 3. Application Architecture

```
Browser Client
     │
     ▼ (Port 8080 in Docker / Port 5173 in dev)
┌─────────────────────────────────────────────┐
│  Nginx Container (production)               │
│  ├── Serves React SPA static assets         │
│  └── Reverse proxies /api/* → backend:5000  │
└─────────────────────┬───────────────────────┘
                      │ internal :5000
                      ▼
┌─────────────────────────────────────────────┐
│  Gunicorn / Flask Backend                   │
│  ├── Application Factory (create_app)       │
│  ├── JWT Authentication (@auth_required)    │
│  ├── Rate Limiting (sliding window)         │
│  ├── Request ID tracing (X-Request-ID)      │
│  ├── REST API blueprints (/api/v1/*)        │
│  └── Service layer (business logic)         │
└─────────────────────┬───────────────────────┘
                      │
          ┌───────────┴────────────┐
          ▼                        ▼
┌──────────────────┐   ┌────────────────────────┐
│ Supabase         │   │ External Providers      │
│ PostgreSQL       │   │ ├── yfinance (market)   │
│ ├── Relational   │   │ ├── Google Gemini (AI)  │
│ │   models (ORM) │   │ └── Email/Webhook       │
│ └── pgvector     │   │     notification chns   │
│     (memories)   │   └────────────────────────┘
└──────────────────┘
```

In development, the Flask backend runs directly (`python run.py`) and the Vite dev server (`npm run dev`) proxies `/api/` requests. In production, both layers are containerized and orchestrated by Docker Compose.

---

## 4. Backend Architecture

### Application Factory

The Flask app is created via `create_app(config_name=None)` in `app/__init__.py`. This factory pattern:
- Loads environment-specific configuration (`DevelopmentConfig`, `ProductionConfig`, `TestingConfig`).
- Initializes SQLAlchemy and Flask-Migrate unbound, then attaches them with `.init_app(app)`.
- Registers all route blueprints and middleware (request ID generation, structured logging, centralized error handling).
- Enables clean isolation between test runs, development, and production — no global state.

### Route Blueprints (`app/routes/`)

| Blueprint | Prefix | Responsibility |
|---|---|---|
| `auth.py` | `/api/v1/auth` | Register, login, token refresh, profile |
| `dashboard.py` | `/api/v1/dashboard` | Read-only aggregated dashboard snapshot |
| `portfolio.py` | `/api/v1/portfolio` | Portfolio positions, valuation, intelligence |
| `watchlist.py` | `/api/v1/watchlist` | Watchlist symbol management |
| `research.py` | `/api/v1/research` | AI research analysis, history |
| `alerts.py` | `/api/v1/alerts` | Alert management, manual check trigger |
| `notifications.py` | `/api/v1/notifications` | Notification records, preferences, endpoints |
| `memory.py` | `/api/v1/memory` | Semantic memory CRUD |
| `monitoring.py` | `/api/v1/monitoring` | Monitoring run history, manual trigger |
| `health.py` | `/api/v1/health` | Liveness and readiness probes |

### Service Layer (`app/services/`)

Services encapsulate all business logic and are the only layer that interacts with models and external providers:

- `portfolio_service.py` — Holdings, cost basis, real-time valuation, gain/loss.
- `watchlist_service.py` — Symbol management, quote enrichment.
- `alert_service.py` — Deterministic rule engine, duplicate prevention.
- `monitoring_service.py` / `monitoring_runner.py` — Batch user monitoring, failure isolation.
- `research_service.py` — CrewAI pipeline orchestration, report persistence.
- `portfolio_intelligence_service.py` — Whole-portfolio AI synthesis.
- `memory_service.py` — Supabase pgvector similarity search and memory storage.
- `embedding_service.py` — Gemini text embedding calls.
- `dashboard_service.py` — Read-only dashboard aggregation.

### Health & Observability

- `GET /api/v1/health/live` — Fast process liveness probe (no external calls).
- `GET /api/v1/health/ready` — Database readiness probe (`SELECT 1` against PostgreSQL).
- `GET /api/v1/version` — Returns `__version__` from `app/version.py`.
- Every request carries an `X-Request-ID` header (generated server-side if absent) that propagates through Nginx → Flask → response for end-to-end tracing.

---

## 5. Frontend Architecture

### Technology Choices

- **React 18 + TypeScript + Vite**: Fast HMR in development, optimized `dist/` bundle for production.
- **Tailwind CSS**: Custom theme with a deep `#090B10` background, glass surfaces, subtle gradients, and financial typography.
- **React Router v6**: Declarative `ProtectedRoute` guards separate the public landing page from the authenticated application shell.
- **Lucide React**: Consistent icon library for navigation, telemetry, and AI features.

### Application Areas

```
/                    → Public Landing Page (Landing.tsx)
/login               → Authentication (Login.tsx)
/register            → Registration (Register.tsx)
/app/dashboard       → Unified Dashboard (read-only snapshot)
/app/portfolio       → Portfolio positions and valuation
/app/watchlist       → Watchlist management
/app/alerts          → Alert management
/app/intelligence    → On-demand portfolio intelligence synthesis
/app/research        → AI equity research workspace
/app/notifications   → Notification records and preferences
/app/settings        → User profile and settings
```

All `/app/*` routes are wrapped in `ProtectedRoute`, which redirects unauthenticated users to `/login`.

### API Client (`src/lib/api.ts`)

A centralized typed API client handles:
- Bearer JWT header injection on every request.
- Uniform error unwrapping and typed response parsing.
- `X-Request-ID` tracing header forwarding.
- Dispatching `window.dispatchEvent(new CustomEvent('aira:unauthorized'))` on 401 responses, which triggers `AuthContext` to clear credentials and redirect to `/login` — preventing infinite loading loops.

### State Management

- **`AuthContext`**: Manages JWT token lifecycle, user identity, and localStorage synchronization. Validates session against `GET /api/v1/auth/me` on app load.
- **`ToastContext`**: Non-intrusive auto-dismissing notifications for all mutations.
- **Domain page state**: Each page manages its own fetch/submit cycles. Mutations follow a strict sequential pattern: mutate → toast → close modal → refresh domain query.

### Currency Handling (INR)

The frontend renders all monetary values in INR (₹). Portfolio positions, valuations, and P&L figures are converted from USD using a real-time USD→INR exchange rate fetched from the financial data layer. The conversion is applied in the service layer before values reach the API response; the frontend does not perform raw symbol substitution.

### Dashboard Read-Only Invariant

`GET /api/v1/dashboard` is strictly read-only. It returns the latest persisted portfolio intelligence snapshot with zero LLM calls, zero financial API calls, and zero database writes. AI synthesis is triggered explicitly from the Intelligence workspace.

---

## 6. Database Architecture

### Single Primary Database: Supabase PostgreSQL

Supabase PostgreSQL is the **single, authoritative database** for all AIRA data:

- **All relational application models** (users, profiles, portfolios, watchlists, research records, intelligence records, alerts, notifications, monitoring) are stored here and accessed via SQLAlchemy ORM with `psycopg2-binary`.
- **Semantic vector memory** (`user_memories`) is natively co-located in the same database using the `pgvector` extension.
- A single connection pool, single backup regime, and single security perimeter cover the entire data tier.

> **MySQL is not part of the runtime architecture.** An earlier phase of development used MySQL as the primary relational database alongside a separate Supabase connection for pgvector. This dual-database architecture was fully superseded — see §16 for the migration history.

### Connection Configuration

The database URI is constructed by `build_database_uri()` in `app/config.py`. It accepts:
- `DATABASE_URL` — a full PostgreSQL connection string (the preferred production method via Supabase).
- Individual `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`, `PGDATABASE` environment variables as an alternative.

The URI is always normalized to `postgresql+psycopg2://` for SQLAlchemy compatibility.

### Schema Migrations

Schema is managed via Flask-Migrate (Alembic). Migration scripts live in `migrations/versions/`. In Docker production deployments, the entrypoint conditionally runs `flask db upgrade` when `RUN_MIGRATIONS=true`.

### Test Isolation

The `TestingConfig` uses in-memory SQLite (`sqlite:///:memory:`) for fast, isolated, deterministic test execution. Tests never touch the Supabase PostgreSQL database.

### Relational Models (`app/models/`)

| Model | Description |
|---|---|
| `User` | Core user identity, password hash, JWT claims source |
| `UserProfile` | 1:1 display name, bio, investment preferences |
| `Portfolio` | Per-user portfolio, holds `PortfolioHolding` rows |
| `PortfolioHolding` | Symbol, quantity, cost basis |
| `WatchlistItem` | Symbol, notes, price target, alert thresholds |
| `ResearchRecord` | Persisted AI research report (facts + analysis + sources) |
| `PortfolioIntelligenceRecord` | Persisted whole-portfolio AI synthesis snapshot |
| `Alert` | Triggered alerts with severity, type, status |
| `AlertMonitoringRun` / `AlertMonitoringLock` | Monitoring orchestration state |
| `NotificationPreference` | Per-user channel toggles, severity filters |
| `NotificationEndpoint` | User-scoped webhook URLs with HMAC signing |
| `NotificationDelivery` | Delivery log per alert per channel (`UNIQUE(alert_id, channel)`) |

---

## 7. Semantic Memory Architecture

### Overview

AIRA implements a user-scoped semantic memory tier using `pgvector` on Supabase PostgreSQL. This enables personalized AI research that reflects each user's investment preferences, risk tolerance, and strategy notes.

### Implementation

- **Table**: `user_memories` in Supabase PostgreSQL.
- **Schema**: Each row stores `user_id` (integer FK), `content` (text), `embedding` (768-dimensional `vector`), `memory_type`, `metadata`, `created_at`.
- **Embeddings**: Generated by `EmbeddingService` calling Google Gemini `text-embedding-004`. Each text string produces a 768-dimensional float vector.
- **Similarity search**: Uses Supabase's `match_user_memories` RPC function, which computes cosine similarity via `pgvector`'s HNSW index. Returns the top-K most similar memories above a configurable similarity threshold.
- **User isolation**: All reads and writes are strictly scoped to `user_id = g.current_user.id` resolved from the verified JWT. No cross-user memory access is possible.

### Usage in Research

When a user triggers AI research, `MemoryService.get_relevant_memories(user_id, query_text)` retrieves the most semantically relevant memories and injects them as personalization context into the CrewAI research crew prompt. This tailors research conclusions without polluting global financial knowledge.

### Memory vs. Research Records

Semantic memories and research records are intentionally separate:
- **Memories** (`user_memories`): Free-form preference and strategy text, embedded for retrieval.
- **Research records** (`research_records`): Structured, immutable AI report snapshots. Research reports are not automatically converted into memories.

---

## 8. Authentication & Security

### JWT Authentication

- **Library**: `PyJWT` with `werkzeug.security` for password hashing (`scrypt`/`pbkdf2`).
- **Token claims**: Minimal — `sub` (user ID integer), `iat` (issued-at UTC), `exp` (expiration UTC). No private data embedded in tokens.
- **Token lifetime**: Configurable via `JWT_ACCESS_TOKEN_EXPIRES_SECONDS` (default: 86400s / 24 hours).
- **Protected routes**: Use the `@auth_required` decorator (`app/common/auth.py`), which validates signatures, confirms user existence in the database, and populates `flask.g.current_user`.

### Multi-Tenant Data Isolation

Every protected endpoint is identity-bounded by `g.current_user`:
- **No client-provided identity trust**: No endpoint accepts a `user_id` from a URL parameter or JSON body to determine data ownership.
- **Database-level scoping**: All queries filter by `user_id = g.current_user.id`.
- **Cross-user responses**: Cross-user lookups return `404 Not Found` to prevent user ID enumeration (IDOR prevention).
- **Cascade deletes**: All user-owned rows use `ON DELETE CASCADE` on the `user_id` foreign key.

### Rate Limiting

Resource-intensive endpoints (AI research, authentication, monitoring triggers) use a sliding-window in-memory rate limiter to prevent API abuse.

### Production Security

- **Passwords**: Never stored in plaintext; never returned in any API response.
- **CORS**: Strict origin configuration; permissive CORS restricted to development only.
- **Secrets**: Loaded exclusively from environment variables. No secrets committed to source code.
- **SSRF protection on webhooks**: User-configured webhook URLs are validated against blocked ranges (loopback, private subnets, cloud metadata IPs), require HTTPS, and enforce a 5-second timeout.
- **HMAC signing**: Outbound webhook requests include `X-AIRA-Signature: sha256=<hex>` when an endpoint `secret_key` is configured.
- **Containers**: Run under unprivileged user `aira` (UID 10001). No `.env` secrets or test dependencies are baked into container layers.

---

## 9. AI Research Architecture

### Agent Framework

AIRA uses **CrewAI** as the multi-agent orchestration framework, backed by **Google Gemini `gemini-2.0-flash`** as the LLM for all agent reasoning.

### Three-Agent Sequential Pipeline

Research is executed as a sequential crew of three specialized agents:

1. **Financial Data Researcher**: Uses CrewAI tools that wrap `FinancialDataService` to fetch real-time quotes, company profiles, historical price data, fundamental financials, valuation metrics, and recent news. Agents never call `yfinance` or external APIs directly.

2. **Investment Analyst**: Analyzes valuation multiples (P/E, P/B, EV/EBITDA), operating margins, balance sheet obligations, and competitive moat strengths based on data retrieved by the Researcher.

3. **Research Synthesizer**: Produces a structured `ResearchReport` JSON object, tailored to retrieved user memory preferences, with citations attached only to verified `SourceMetadata` objects.

### Evidence-Based Output: Fact vs. Analysis Separation

The `ResearchReport` enforces a strict separation:
- **`facts`**: Pre-fetched ground-truth metrics (`current_price`, `pe_ratio`, `market_cap`, `profit_margins`, `total_debt`, `sector`, `industry`) pulled directly from `FinancialDataService` — never LLM-generated.
- **`fundamentals`, `valuation`, `market_context`, `risks`, `opportunities`**: AI analytical conclusions derived by reasoning over verified facts.
- **`sources`**: Assembled from authenticated `SourceMetadata` objects attached to financial entities. The LLM cannot invent citations.

Malformed or unparseable LLM output raises a `ValueError` and results in a safe error response rather than returning fabricated claims under HTTP 200.

### Portfolio Intelligence

`PortfolioIntelligenceService` runs a separate CrewAI crew over the user's entire portfolio and watchlist to produce whole-portfolio risk, sector concentration analysis, and prioritized research recommendations. Results are persisted as immutable `PortfolioIntelligenceRecord` snapshots. The dashboard reads the latest persisted snapshot with zero LLM calls.

---

## 10. Financial Data Architecture

### Provider Abstraction

All financial data access goes through a two-layer abstraction:

1. **`BaseFinancialProvider`** (`app/services/financial/base.py`): Abstract interface defining the data contract.
2. **`YFinanceProvider`** (`app/services/financial/provider.py`): Concrete implementation wrapping `yfinance`. Normalizes raw Yahoo Finance responses into typed domain objects: `MarketQuote`, `CompanyProfile`, `KeyMetrics`, `HistoricalPrices`, `NewsArticle`.

### `FinancialDataService`

`app/services/financial/service.py` is the single point of access for all financial data:
- TTL caching reduces redundant API calls for frequently requested data.
- Symbol validation and normalization (e.g., NSE/BSE ticker formatting).
- Defensive handling for `yfinance` schema drift and provider errors.
- CrewAI tools wrap `FinancialDataService` methods — agents never bypass this abstraction.

### INR Currency Handling

AIRA is designed for Indian investors. Financial data from `yfinance` is denominated in USD (for US equities) or the native currency for Indian equities. A real-time USD→INR exchange rate is fetched from the financial data provider and applied in the service layer before values are returned via the API. The frontend renders all monetary values with the `₹` symbol. The conversion is a true rate-based calculation, not a symbol substitution.

### Data Provenance

Every financial entity returned by `FinancialDataService` carries `SourceMetadata` (data source identifier, retrieval timestamp, symbol). This metadata is attached to research reports as verifiable citations.

### Test Strategy

Automated tests mock the provider layer for fast, deterministic, offline execution. Live `yfinance` calls are not made during CI test runs.

---

## 11. Portfolio & Watchlist Architecture

### Portfolio

Each user has one `Portfolio` containing multiple `PortfolioHolding` rows (symbol, quantity, cost basis per share). `PortfolioService` computes:
- Current market value via live `FinancialDataService` quotes.
- Unrealized gain/loss (absolute and percentage) per holding and portfolio total.
- Sector and weight concentration.

Portfolio valuations are snapshot calculations performed on each request — they are not stored as pre-computed values.

### Watchlist

`WatchlistItem` records hold a symbol, optional notes, price target, and configurable alert thresholds (`gain_threshold_pct`, `loss_threshold_pct`, `price_move_threshold_pct`). `WatchlistService` enriches each item with the current live quote on demand.

### Portfolio Intelligence

`PortfolioIntelligenceService` synthesizes the full portfolio and watchlist into a whole-portfolio AI narrative on user demand. The output (`PortfolioIntelligenceRecord`) is an immutable snapshot containing:
- Verified numerical facts (valuations, weights, gain/loss) in a structured `facts` column.
- AI-generated qualitative analysis (`portfolio_overview`, `portfolio_risks`, `portfolio_opportunities`, `watchlist_priorities`, `recommended_research`).

A history API allows users to retrieve, compare, and delete past intelligence snapshots.

---

## 12. Alerts, Monitoring & Notifications

### Alert Detection (Deterministic)

`AlertService` evaluates deterministic Python rules against live financial data — no LLM involved:

| Alert Type | Trigger Condition |
|---|---|
| `data_quality` | Live quote unavailable for a holding |
| `portfolio_gain` | Holding unrealized gain ≥ threshold (default +10%, critical at +20%) |
| `portfolio_loss` | Holding unrealized loss ≤ threshold (default -10%, critical at -20%) |
| `price_move` | Daily price movement ≥ threshold (default ±5%) |
| `watchlist_move` | Watchlist item daily move ≥ item-specific threshold |

Duplicate prevention: before creating an alert, the engine checks for an existing active non-dismissed alert for the unique `(user_id, symbol, alert_type)` combination.

### Automated Monitoring

`MonitoringService` orchestrates scheduled batch execution across all users with `alerts_enabled = True`:
- Each user is processed in an isolated transaction block — one user's failure does not interrupt others.
- `AlertMonitoringRun` persists run metadata (start time, users checked, alerts created, users failed).
- `AlertMonitoringLock` prevents concurrent monitoring runs.
- Monitoring can be triggered by any external scheduler: cron, systemd timer, Windows Task Scheduler, or Celery.

### Notification Delivery

`NotificationService` routes fired alerts to configured channels:
- **`InAppNotificationProvider`** — default in-app delivery.
- **`EmailNotificationProvider`** — formats alert subjects and bodies; fails gracefully if API key is absent.
- **`WebhookNotificationProvider`** — HTTPS POST with optional HMAC signing; SSRF-protected (see §8).

`NotificationDelivery` enforces `UNIQUE(alert_id, channel)` — repeated monitoring runs on unchanged data never create duplicate notification attempts.

### User Notification Preferences

`NotificationPreference` (1:1 with `User`) controls:
- Per-channel toggles: `in_app_enabled`, `email_enabled`, `webhook_enabled`.
- `minimum_severity` filter: `info`, `warning`, `critical`.
- Optional `alert_types` allowlist.

---

## 13. Research Persistence & Intelligence

### Research History

Every successfully completed AI research report is persisted to `research_records` with:
- `symbol`, `company`, `query`, `summary` — lightweight identifiers.
- `facts` (JSONB) — verified pre-fetched metrics.
- `sources` (JSONB) — authenticated source metadata.
- `fundamentals`, `valuation`, `market_context`, `risks`, `opportunities`, `user_context` — AI analysis fields.
- `created_at` — immutable timestamp.

Research records are immutable snapshots. Persistence occurs only after successful validation — failed or malformed research runs persist nothing.

### Research History API

| Endpoint | Behavior |
|---|---|
| `POST /api/v1/research/analyze` | Runs CrewAI pipeline, persists result, returns report |
| `GET /api/v1/research/history` | Paginated lightweight summaries (bounded at 100 per page) |
| `GET /api/v1/research/history/<id>` | Full report by ID |
| `DELETE /api/v1/research/history/<id>` | Delete owned record |

All operations strictly scoped to `g.current_user.id`.

### Portfolio Intelligence History API

| Endpoint | Behavior |
|---|---|
| `POST /api/v1/portfolio/intelligence/generate` | Runs synthesis crew, persists snapshot |
| `GET /api/v1/portfolio/intelligence/history` | Paginated lightweight summaries |
| `GET /api/v1/portfolio/intelligence/history/<id>` | Full snapshot by ID |
| `DELETE /api/v1/portfolio/intelligence/history/<id>` | Delete owned snapshot |
| `GET /api/v1/dashboard` | Returns latest snapshot (read-only, zero AI calls) |

---

## 14. Production & Deployment Architecture

### Docker Compose Stack

In production (or local production testing), Docker Compose orchestrates three services:

| Service | Image | Port |
|---|---|---|
| `aira-frontend` | Nginx (multi-stage: Node 20 build → nginx:1.27-alpine) | 8080 |
| `aira-backend` | python:3.10-slim + Gunicorn | 5000 (internal) |

> **Note:** The earlier Docker Compose included a MySQL container (`aira-mysql`). This is no longer part of the runtime — Supabase PostgreSQL is the database, accessed over the network.

### Backend Container

- Base: `python:3.10-slim`.
- Process: Gunicorn (`--worker-class gthread`, 2 workers, 4 threads per worker).
- Security: Unprivileged user `aira` (UID 10001). No `.env` secrets or test dependencies in image layers.
- Entrypoint: `docker/entrypoint.sh` — conditionally runs `flask db upgrade` (controlled by `RUN_MIGRATIONS=true`), then `exec`s Gunicorn for proper SIGTERM propagation.

### Frontend Container

- Multi-stage build: Node 20 compiles the React/TypeScript bundle; Nginx serves the `dist/` assets.
- SPA routing: `try_files $uri $uri/ /index.html;` handles all client-side routes.
- Reverse proxy: `/api/` traffic forwarded to `backend:5000` with header forwarding (`X-Real-IP`, `X-Forwarded-For`, `X-Request-ID`).

### Environment Configuration

All secrets and connection strings are loaded from environment variables. Required variables:
- `DATABASE_URL` or (`PGUSER` + `PGPASSWORD` + `PGHOST` + `PGPORT` + `PGDATABASE`)
- `SUPABASE_URL`, `SUPABASE_KEY` (for pgvector memory RPC)
- `GOOGLE_API_KEY` (Gemini AI)
- `SECRET_KEY` (Flask session / JWT signing)
- `JWT_ACCESS_TOKEN_EXPIRES_SECONDS` (optional, default 86400)

Missing database configuration causes immediate startup failure (fail-fast). There is no silent fallback to SQLite in production.

### Development Setup

```
# Backend (from project root)
python run.py          # Flask dev server on :5000

# Frontend (from frontend/)
npm run dev            # Vite dev server on :5173 with /api proxy to :5000
```

### CI Pipeline

GitHub Actions (`.github/workflows/ci.yml`) enforces:
- Backend: `pytest` (195+ tests across all service and route layers).
- Frontend: TypeScript typecheck (`tsc --noEmit`), Vitest component/integration tests, production build.
- E2E: Playwright browser tests for critical authentication and navigation flows.

---

## 15. Product / Landing Architecture

The public landing page at `/` is a standalone React page (`Landing.tsx`) that:
- Loads with zero backend or AI API calls.
- Uses 100% deterministic, illustrative scenario data for all interactive simulators.
- Communicates AIRA's research workflow through interactive visual components: `HeroIntelligenceEngine`, `ArchitectureCircuit`, `MultiAgentNetworkVisual`, `MarketTerminalChart`, `PortfolioAllocationVisual`, `DataTransformationFlow`, `EvidenceGroundingFlow`.
- Includes full SEO metadata: `<title>`, `<meta description>`, JSON-LD structured data, Open Graph tags, `robots.txt`, `sitemap.xml`.
- Tailwind custom keyframe animations (`pulse-slow`, `scanline`, `shimmer`, `float`, `data-pulse`) with `@media (prefers-reduced-motion: reduce)` overrides.

The landing page is fully decoupled from the authenticated application shell. No authentication state is required to visit it.

---

## 16. Major Architectural Evolution

### MySQL → Supabase PostgreSQL (ADR-002 → ADR-026)

**Previous architecture (superseded):**
- MySQL (via `PyMySQL` + SQLAlchemy) was the primary relational database for all application data.
- Supabase PostgreSQL + `pgvector` was a separate, secondary database used exclusively for semantic memory embeddings.
- Docker Compose included a MySQL 8.0 container.

**Final architecture:**
- Supabase PostgreSQL is the single authoritative database for all AIRA data — both relational models and vector memory are co-located.
- MySQL and `PyMySQL` are completely removed from the runtime.
- A single connection pool, one backup regime, and one security perimeter cover the entire data tier.
- The `build_database_uri()` function (previously named `build_mysql_uri`) now constructs only PostgreSQL connection strings.

This migration eliminated dual-engine connection pooling overhead, simplified deployment, and removed the need to run a local MySQL container.

---

## 17. Current Architectural Principles

These principles guide all future development on AIRA:

1. **Single database.** Supabase PostgreSQL is the one authoritative store. Introduce a new data technology only when there is a compelling, irreplaceable capability justification.

2. **Deterministic calculations, AI for reasoning.** All financial arithmetic (portfolio valuation, gain/loss, alert threshold evaluation) uses deterministic Python and SQL. LLMs are used only for qualitative synthesis. Never use an LLM to compute a number.

3. **Facts are sacred.** Financial metrics in research reports are pre-fetched from `FinancialDataService` and attached verbatim. LLMs cannot override, invent, or round reported facts. Malformed LLM output fails loudly rather than silently substituting generic claims.

4. **Zero client identity trust.** No endpoint accepts a client-provided `user_id` to determine data ownership. Every operation is bounded by `g.current_user` from a verified JWT token.

5. **Isolation at every boundary.** User A's portfolios, memories, research, alerts, and notifications are inaccessible to User B — enforced at the query level, not convention.

6. **Read-only dashboard.** `GET /api/v1/dashboard` never triggers AI calls, external API calls, or database writes. AI synthesis is always an explicit, user-initiated action.

7. **Fail fast on configuration.** Missing required environment variables (database URL, API keys) cause immediate startup failure. There is no silent fallback to a default that could corrupt production data.

8. **Provider abstraction.** All external data (financial, AI, notifications) is accessed through defined interfaces. Concrete implementations can be swapped without touching business logic or tests.

9. **Test isolation.** Automated tests use in-memory SQLite and mocked providers. They never touch Supabase PostgreSQL, Gemini, or live `yfinance` endpoints.

10. **Immutable snapshots.** Persisted research reports and portfolio intelligence records are immutable. Historical records always reflect the exact state at the time of generation.
