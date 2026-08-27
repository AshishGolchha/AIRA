# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, personalized memory, user watchlists, portfolio valuation tracking, deterministic alerts, and automated monitoring.

---

## Current Phase

**Phase 11 — Automated Alert Monitoring & Notification Foundation**

Phase 11 establishes the automated monitoring orchestration and notification delivery foundation across eligible user accounts:
- **Automated Monitoring Service (`MonitoringService`)**: Discovers eligible users (`User.alerts_enabled = True`) and executes batch alert checks with strict per-user transaction isolation (`db.session.rollback()` on user failure). One user's error never halts the monitoring run.
- **Monitoring Run Tracking (`AlertMonitoringRun`)**: Records execution statistics (`status`, `users_checked`, `users_succeeded`, `users_failed`, `alerts_generated`, `error_summary`, `started_at`, `completed_at`).
- **Decoupled Notification Abstraction (`NotificationService` & `BaseNotificationProvider`)**: Decouples alert detection from notification delivery. Provides channel-level idempotency via a `UNIQUE(alert_id, channel)` constraint on `NotificationDelivery` to eliminate duplicate notification attempts.
- **Default In-App Delivery Channel (`InAppNotificationProvider`)**: Serves as the foundational notification provider, establishing the exact interface for future channels (Email, SMS, Mobile Push) without altering alert detection rules.
- **Deterministic Math & Zero LLM Alert Generation**: All alert triggers (price moves, gain/loss thresholds, data quality missing quotes) are evaluated deterministically in Python. Zero LLM involvement in numerical rule decisions.
- **Strict Multi-Tenant Security**: Automated monitoring resolves user IDs directly from database query of eligible users. Client-controlled IDs can never trigger or influence batch monitoring.

---

## Technology Stack

- **Runtime**: Python 3.10+
- **Web Framework**: Flask 3.x
- **Agent Framework**: CrewAI
- **LLM**: Google Gemini (`gemini/gemini-2.0-flash`)
- **Embeddings**: Google Gemini API (`gemini-embedding-2`, 768 dimensions)
- **Authentication & Security**: PyJWT, Werkzeug Security
- **Relational Database & Migrations**: MySQL, SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Vector Database**: Supabase PostgreSQL + `pgvector`
- **Market Data Provider**: `yfinance` (Yahoo Finance API)
- **Testing**: Pytest (isolated in-memory SQLite + mock financial, vector, & agent services)
- **Configuration**: Python-dotenv

---

## Architecture Overview

```
AIRA/
├── app/
│   ├── common/
│   │   ├── __init__.py
│   │   └── auth.py           # Shared JWT generation, verification & @auth_required decorator
│   ├── config.py             # Environment configurations, alert thresholds, & monitoring settings
│   ├── extensions.py         # Extension singletons (SQLAlchemy, Migrate)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── alert.py          # Alert persistent SQLAlchemy model
│   │   ├── base.py           # Base model mixins (TimestampMixin)
│   │   ├── financial.py      # Normalized research dataclasses, ResearchReport, & PortfolioIntelligenceReport
│   │   ├── monitoring.py     # AlertMonitoringRun execution tracking model
│   │   ├── notification.py   # NotificationDelivery delivery tracking model
│   │   ├── portfolio.py      # PortfolioHolding persistent SQLAlchemy model
│   │   ├── research.py       # ResearchRecord persistent SQLAlchemy model
│   │   ├── user.py           # User & UserProfile SQLAlchemy models
│   │   └── watchlist.py      # WatchlistItem persistent SQLAlchemy model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── alerts.py         # Alert routes (check, list, get, read, dismiss)
│   │   ├── auth.py           # Authentication routes (register, login, me)
│   │   ├── health.py         # Versioned health check endpoint (/api/v1/health)
│   │   ├── memory.py         # User memory routes (create, list, search, delete)
│   │   ├── portfolio.py      # Portfolio holdings CRUD, valuation snapshot, & intelligence endpoints
│   │   ├── profile.py        # User profile routes (get, update)
│   │   ├── research.py       # Research routes (analyze, history, profile, quote, history, financials, news, search)
│   │   └── watchlist.py      # Watchlist CRUD & priority filtering endpoints
│   └── services/
│       ├── __init__.py
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── crew.py       # CrewAI 3-agent research and portfolio intelligence crew definitions
│       │   └── tools.py      # CrewAI tools wrapping FinancialDataService
│       ├── alert_service.py     # Deterministic alert detection engine & management
│       ├── embedding_service.py # Gemini gemini-embedding-2 provider (768 dims)
│       ├── memory_service.py    # User-scoped semantic memory service
│       ├── monitoring_service.py # Automated batch alert monitoring orchestrator
│       ├── notifications/
│       │   ├── __init__.py      # Notification layer export
│       │   ├── base.py          # BaseNotificationProvider interface
│       │   ├── in_app.py        # InAppNotificationProvider implementation
│       │   └── service.py       # NotificationService with delivery tracking & idempotency
│       ├── portfolio_intelligence_service.py # Orchestrator for personalized portfolio & watchlist intelligence
│       ├── portfolio_service.py # Portfolio holding management & valuation calculation
│       ├── research_service.py  # Research pipeline orchestrator with persistence
│       ├── watchlist_service.py # Watchlist management & symbol resolution
│       └── financial/
│           ├── __init__.py
│           ├── base.py       # BaseFinancialProvider abstract interface
│           ├── provider.py   # YFinanceProvider implementation
│           └── service.py    # FinancialDataService with TTL caching & symbol validation
├── docs/
│   └── architecture-decisions/
│       ├── ADR-001-flask-application-factory.md
│       ├── ADR-002-mysql-sqlalchemy-database-strategy.md
│       ├── ADR-003-multi-user-data-isolation.md
│       ├── ADR-004-future-memory-architecture.md
│       ├── ADR-005-jwt-authentication-strategy.md
│       ├── ADR-006-persistent-user-memory-supabase-pgvector.md
│       ├── ADR-007-financial-data-provider-architecture.md
│       ├── ADR-008-ai-research-agent-crewai-architecture.md
│       ├── ADR-009-evidence-based-research-workflow.md
│       ├── ADR-010-research-persistence-and-history.md
│       ├── ADR-011-user-watchlist-and-portfolio-foundation.md
│       ├── ADR-012-personalized-portfolio-intelligence.md
│       ├── ADR-013-alert-detection-and-monitoring-foundation.md
│       └── ADR-014-automated-alert-monitoring-and-notification-foundation.md
├── migrations/               # MySQL Alembic database migration scripts
│   └── versions/
│       ├── 0001_create_users_and_user_profiles.py
│       ├── 0002_create_research_records.py
│       ├── 0003_create_watchlist_and_portfolio.py
│       ├── 0004_create_alerts.py
│       └── 0005_create_monitoring_and_notifications.py
├── supabase/                 # Supabase pgvector schema and migration scripts
│   └── migrations/
│       └── 001_create_user_memories.sql
├── tests/
│   ├── conftest.py           # Test fixtures with isolated SQLite database
│   ├── unit/
│   │   ├── test_ai_tools.py          # CrewAI financial tools unit tests
│   │   ├── test_alert_service.py     # Alert detection rules & CRUD unit tests
│   │   ├── test_config.py            # Configuration and connection URI tests
│   │   ├── test_embedding_service.py # Embedding service unit tests
│   │   ├── test_financial_provider.py # Financial models & provider unit tests
│   │   ├── test_financial_service.py  # Financial service & caching unit tests
│   │   ├── test_memory_service.py     # Memory service unit tests
│   │   ├── test_monitoring_service.py # MonitoringService batch & isolation tests
│   │   ├── test_notification_service.py # NotificationService idempotency & delivery tests
│   │   ├── test_portfolio_intelligence_service.py # Portfolio intelligence unit tests
│   │   ├── test_portfolio_model.py    # PortfolioHolding model unit tests
│   │   ├── test_portfolio_service.py  # PortfolioService calculation unit tests
│   │   ├── test_research_model.py     # ResearchRecord model unit tests
│   │   ├── test_research_service.py   # Research orchestration service unit tests
│   │   ├── test_watchlist_model.py    # WatchlistItem model unit tests
│   │   └── test_watchlist_service.py  # WatchlistService unit tests
│   └── integration/
│       ├── test_ai_research.py       # AI research workflow, facts grounding, & personalization tests
│       ├── test_alerts.py            # Alerts check, list, get, read, dismiss & isolation tests
│       ├── test_auth.py              # Registration, login, auth context tests
│       ├── test_health.py            # Health endpoint, Request ID, and Error handling tests
│       ├── test_memory.py            # Memory CRUD, vector search, and isolation tests
│       ├── test_monitoring.py        # Automated batch monitoring integration & idempotency tests
│       ├── test_portfolio.py         # Portfolio CRUD, snapshot calculations, and isolation tests
│       ├── test_portfolio_intelligence.py # Portfolio intelligence endpoint & personalization tests
│       ├── test_profile.py           # Profile endpoints & multi-user isolation tests
│       ├── test_research.py          # Financial data endpoints integration tests
│       ├── test_research_history.py  # Research history & multi-tenant persistence tests
│       └── test_watchlist.py         # Watchlist CRUD, priority filtering, and isolation tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── requirements.txt          # Minimal dependencies
└── run.py                    # Application entry point
```

---

## API Endpoints

All endpoints are versioned under `/api/v1/`.

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | No | Service health check |
| `POST` | `/api/v1/auth/register` | No | Register a new user and profile |
| `POST` | `/api/v1/auth/login` | No | Authenticate credentials and receive JWT |
| `GET` | `/api/v1/auth/me` | Yes (`Bearer <token>`) | Get current authenticated user details |
| `GET` | `/api/v1/profile` | Yes (`Bearer <token>`) | Retrieve current user's profile |
| `PUT` | `/api/v1/profile` | Yes (`Bearer <token>`) | Update current user's profile |
| `POST` | `/api/v1/memory` | Yes (`Bearer <token>`) | Store a new user memory and vector embedding |
| `GET` | `/api/v1/memory` | Yes (`Bearer <token>`) | List recent memories for authenticated user |
| `GET` | `/api/v1/memory/search` | Yes (`Bearer <token>`) | Semantic vector search (`?q=...&limit=...`) |
| `DELETE` | `/api/v1/memory/<id>` | Yes (`Bearer <token>`) | Delete a memory owned by authenticated user |
| `POST` | `/api/v1/watchlist` | Yes (`Bearer <token>`) | Add a security to user's personal watchlist |
| `GET` | `/api/v1/watchlist` | Yes (`Bearer <token>`) | List watchlist items (supports `?priority=high`) |
| `GET` | `/api/v1/watchlist/<id>` | Yes (`Bearer <token>`) | Retrieve a single watchlist item |
| `PUT` | `/api/v1/watchlist/<id>` | Yes (`Bearer <token>`) | Update watchlist item notes or priority |
| `DELETE` | `/api/v1/watchlist/<id>` | Yes (`Bearer <token>`) | Remove a security from personal watchlist |
| `POST` | `/api/v1/portfolio/holdings` | Yes (`Bearer <token>`) | Add a portfolio holding position |
| `GET` | `/api/v1/portfolio/holdings` | Yes (`Bearer <token>`) | List all holdings for authenticated user |
| `GET` | `/api/v1/portfolio/holdings/<id>` | Yes (`Bearer <token>`) | Retrieve a single portfolio holding |
| `PUT` | `/api/v1/portfolio/holdings/<id>` | Yes (`Bearer <token>`) | Update holding quantity, cost, or notes |
| `DELETE` | `/api/v1/portfolio/holdings/<id>` | Yes (`Bearer <token>`) | Delete a portfolio holding |
| `GET` | `/api/v1/portfolio/snapshot` | Yes (`Bearer <token>`) | Calculate real-time portfolio valuation & gain/loss |
| `POST` | `/api/v1/portfolio/intelligence` | Yes (`Bearer <token>`) | Generate personalized portfolio & watchlist intelligence |
| `POST` | `/api/v1/alerts/check` | Yes (`Bearer <token>`) | Run deterministic alert rules against holdings & watchlist |
| `GET` | `/api/v1/alerts` | Yes (`Bearer <token>`) | List alerts (`?unread_only=true&include_dismissed=false`) |
| `GET` | `/api/v1/alerts/<id>` | Yes (`Bearer <token>`) | Retrieve a single alert (404 if not owned) |
| `PUT` | `/api/v1/alerts/<id>/read` | Yes (`Bearer <token>`) | Mark alert as read |
| `PUT` | `/api/v1/alerts/<id>/dismiss` | Yes (`Bearer <token>`) | Dismiss alert |
| `POST` | `/api/v1/research/analyze` | Yes (`Bearer <token>`) | Trigger evidence-based AI research and persist report |
| `GET` | `/api/v1/research/history` | Yes (`Bearer <token>`) | List paginated research history summaries |
| `GET` | `/api/v1/research/history/<id>` | Yes (`Bearer <token>`) | Retrieve a full completed research report |
| `DELETE` | `/api/v1/research/history/<id>` | Yes (`Bearer <token>`) | Delete a research report owned by user |
| `GET` | `/api/v1/research/search` | Yes (`Bearer <token>`) | Resolve company name to ticker symbol (`?q=...`) |
| `GET` | `/api/v1/research/company/<symbol>` | Yes (`Bearer <token>`) | Retrieve company overview & business summary |
| `GET` | `/api/v1/research/company/<symbol>/quote` | Yes (`Bearer <token>`) | Retrieve latest price quote, day range, & volume |
| `GET` | `/api/v1/research/company/<symbol>/history` | Yes (`Bearer <token>`) | Retrieve OHLCV historical prices (`?period=1mo&interval=1d`) |
| `GET` | `/api/v1/research/company/<symbol>/financials` | Yes (`Bearer <token>`) | Retrieve financial statements (`?type=income_statement`) |
| `GET` | `/api/v1/research/company/<symbol>/metrics` | Yes (`Bearer <token>`) | Retrieve valuation & operational ratios (PE, P/B, Beta) |
| `GET` | `/api/v1/research/company/<symbol>/news` | Yes (`Bearer <token>`) | Retrieve recent company news articles (`?limit=5`) |

---

## Local Setup

### 1. Clone & Navigate
```bash
cd AIRA
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```ini
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://aira_user:aira_password@localhost:3306/aira_db
JWT_SECRET_KEY=your-secure-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES_SECONDS=86400

# Supabase (pgvector memory)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Gemini AI (LLM & Embeddings)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_LLM_MODEL=gemini/gemini-2.0-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-2

# Alert & Monitoring Thresholds (Optional)
ALERT_PRICE_MOVE_THRESHOLD_PERCENT=5.0
ALERT_PORTFOLIO_GAIN_LOSS_THRESHOLD_PERCENT=10.0
ALERT_MONITORING_ENABLED=true
NOTIFICATION_ENABLED=true
```

### 5. Run Database Migrations
- **MySQL Migrations**:
  ```bash
  flask db upgrade
  ```
- **Supabase pgvector Schema**:
  Execute `supabase/migrations/001_create_user_memories.sql` in the Supabase SQL Editor.

---

## Running Automated Monitoring
To execute an automated alert monitoring run from a CLI, background script, or scheduler:
```python
from app import create_app
from app.services.monitoring_service import MonitoringService

app = create_app()
with app.app_context():
    service = MonitoringService()
    results = service.run_alert_monitoring()
    print("Monitoring Run Stats:", results)
```

---

## Running Tests

Run the automated test suite with pytest:
```bash
python -m pytest -v
```

All 131 automated tests run deterministically against an isolated in-memory SQLite database (`sqlite:///:memory:`) and mock external services.
