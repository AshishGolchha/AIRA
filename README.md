# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, personalized memory, user watchlists, and portfolio valuation tracking.

---

## Current Phase

**Phase 9 — Personalized Portfolio & Watchlist Intelligence**

Phase 9 implements the personalized intelligence layer unifying the investor's actual portfolio holdings, watchlist securities, profile preferences, private semantic memories, and prior research history:
- **Personalized Portfolio Intelligence Service (`PortfolioIntelligenceService`)**: Assembles deterministic holding valuations, concentration weights, watchlist quotes, profile preferences, and private semantic memories into a compact factual dataset.
- **Evidence-Grounded CrewAI Intelligence**: Extends the 3-agent research crew (`Portfolio Researcher`, `Investment Analyst`, `Personalized Research Synthesizer`) to evaluate portfolio concentration risks, opportunities, and watchlist priorities without fabricating numerical data.
- **Deterministic Math & Zero LLM Arithmetic**: All holding valuations, cost bases, unrealized gain/loss amounts, and portfolio weights are calculated deterministically in Python using `Decimal`.
- **Strict Multi-Tenant Isolation**: All intelligence inputs (portfolio, watchlist, profile, memories, research history) are resolved exclusively for `g.current_user.id` from verified JWT claims.
- **Safe Empty-State & Failure Resiliency**: Gracefully handles accounts with empty portfolios/watchlists and safely fails on malformed AI model output with standardized 500 error envelopes.

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
│   ├── config.py             # Environment configurations (Development, Production, Testing)
│   ├── extensions.py         # Extension singletons (SQLAlchemy, Migrate)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # Base model mixins (TimestampMixin)
│   │   ├── financial.py      # Normalized research dataclasses, ResearchReport, & PortfolioIntelligenceReport
│   │   ├── portfolio.py      # PortfolioHolding persistent SQLAlchemy model
│   │   ├── research.py       # ResearchRecord persistent SQLAlchemy model
│   │   ├── user.py           # User & UserProfile SQLAlchemy models
│   │   └── watchlist.py      # WatchlistItem persistent SQLAlchemy model
│   ├── routes/
│   │   ├── __init__.py
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
│       ├── embedding_service.py # Gemini gemini-embedding-2 provider (768 dims)
│       ├── memory_service.py    # User-scoped semantic memory service
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
│       └── ADR-012-personalized-portfolio-intelligence.md
├── migrations/               # MySQL Alembic database migration scripts
│   └── versions/
│       ├── 0001_create_users_and_user_profiles.py
│       ├── 0002_create_research_records.py
│       └── 0003_create_watchlist_and_portfolio.py
├── supabase/                 # Supabase pgvector schema and migration scripts
│   └── migrations/
│       └── 001_create_user_memories.sql
├── tests/
│   ├── conftest.py           # Test fixtures with isolated SQLite database
│   ├── unit/
│   │   ├── test_ai_tools.py          # CrewAI financial tools unit tests
│   │   ├── test_config.py            # Configuration and connection URI tests
│   │   ├── test_embedding_service.py # Embedding service unit tests
│   │   ├── test_financial_provider.py # Financial models & provider unit tests
│   │   ├── test_financial_service.py  # Financial service & caching unit tests
│   │   ├── test_memory_service.py     # Memory service unit tests
│   │   ├── test_portfolio_intelligence_service.py # Portfolio intelligence unit tests
│   │   ├── test_portfolio_model.py    # PortfolioHolding model unit tests
│   │   ├── test_portfolio_service.py  # PortfolioService calculation unit tests
│   │   ├── test_research_model.py     # ResearchRecord model unit tests
│   │   ├── test_research_service.py   # Research orchestration service unit tests
│   │   ├── test_watchlist_model.py    # WatchlistItem model unit tests
│   │   └── test_watchlist_service.py  # WatchlistService unit tests
│   └── integration/
│       ├── test_ai_research.py       # AI research workflow, facts grounding, & personalization tests
│       ├── test_auth.py              # Registration, login, auth context tests
│       ├── test_health.py            # Health endpoint, Request ID, and Error handling tests
│       ├── test_memory.py            # Memory CRUD, vector search, and isolation tests
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
```

### 5. Run Database Migrations
- **MySQL Migrations**:
  ```bash
  flask db upgrade
  ```
- **Supabase pgvector Schema**:
  Execute `supabase/migrations/001_create_user_memories.sql` in the Supabase SQL Editor.

---

## Running the Application

Start the Flask development server:
```bash
python run.py
```

---

## Running Tests

Run the automated test suite with pytest:
```bash
python -m pytest -v
```

All 107 automated tests run deterministically against an isolated in-memory SQLite database (`sqlite:///:memory:`) and mock external services.
