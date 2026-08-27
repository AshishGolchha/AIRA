# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, and personalized portfolio tracking.

---

## Current Phase

**Phase 6 — Evidence-Based Research Workflow & Reliable Research Output**

Phase 6 hardens AIRA's multi-agent research pipeline into a traceable, evidence-grounded intelligence system:
- **Fact vs. Analysis Separation**: The structured output explicitly isolates verified `facts` (provided directly from `FinancialDataService`) from AI analytical interpretations (`fundamentals`, `valuation`, `market_context`, `risks`, `opportunities`).
- **Elimination of Fabricated Fallbacks**: Removed silent fallback behavior that previously manufactured generic claims upon unparseable LLM output. Malformed AI responses fail safely with a standardized error response (`INTERNAL_SERVER_ERROR`).
- **Verified Source Provenance**: `sources` in `ResearchReport` is assembled strictly from verified `SourceMetadata` entries attached to actual financial entities, barring the LLM from inventing citations or URLs.
- **Pre-Fetched Factual Context**: Ground-truth financials are pre-fetched and injected directly into agent reasoning tasks, minimizing numerical hallucinations.
- **Strict Multi-Tenant Isolation**: Memory personalization continues to resolve strictly from `g.current_user.id` (JWT), rejecting client-supplied `user_id` parameters.

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
│   │   ├── financial.py      # Normalized research dataclasses & ResearchReport (with facts & sources)
│   │   └── user.py           # User & UserProfile SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes (register, login, me)
│   │   ├── health.py         # Versioned health check endpoint (/api/v1/health)
│   │   ├── memory.py         # User memory routes (create, list, search, delete)
│   │   ├── profile.py        # User profile routes (get, update)
│   │   └── research.py       # Research & AI analysis routes (analyze, profile, quote, history, financials, news, search)
│   └── services/
│       ├── __init__.py
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── crew.py       # CrewAI 3-agent sequential research crew definition
│       │   └── tools.py      # CrewAI tools wrapping FinancialDataService
│       ├── embedding_service.py # Gemini gemini-embedding-2 provider (768 dims)
│       ├── memory_service.py    # User-scoped semantic memory service
│       ├── research_service.py  # Evidence-grounded research pipeline orchestrator
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
│       └── ADR-009-evidence-based-research-workflow.md
├── migrations/               # MySQL Alembic database migration scripts
│   └── versions/
│       └── 0001_create_users_and_user_profiles.py
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
│   │   └── test_research_service.py   # Research orchestration service unit tests
│   └── integration/
│       ├── test_ai_research.py       # AI research workflow, facts grounding, & personalization tests
│       ├── test_auth.py              # Registration, login, auth context tests
│       ├── test_health.py            # Health endpoint, Request ID, and Error handling tests
│       ├── test_memory.py            # Memory CRUD, vector search, and isolation tests
│       ├── test_profile.py           # Profile endpoints & multi-user isolation tests
│       └── test_research.py          # Financial research endpoints integration tests
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
| `POST` | `/api/v1/research/analyze` | Yes (`Bearer <token>`) | Trigger evidence-based AI research on a company/symbol |
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

All 66 automated tests run deterministically against an isolated in-memory SQLite database (`sqlite:///:memory:`) and mock external services.
