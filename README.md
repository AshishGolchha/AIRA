# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, and personalized portfolio tracking.

---

## Current Phase

**Phase 1 — Production-Oriented Backend Foundation**

Phase 1 delivers the foundational backend architecture, ensuring clean dependency management, environment configuration, database integration, structured JSON error handling, request ID tracing, and an isolated test harness.

> **Important Scope Clarification**:
> Phase 1 is strictly a backend foundation. It does **not** yet perform investment research, stock analysis, Gemini LLM reasoning, CrewAI multi-agent orchestration, or semantic memory retrieval.

---

## Technology Stack

- **Runtime**: Python 3.10+
- **Web Framework**: Flask 3.x
- **ORM & Migrations**: SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate
- **Primary Database**: MySQL (via PyMySQL driver)
- **Testing**: Pytest (utilizing isolated in-memory SQLite)
- **Configuration**: Python-dotenv

---

## Architecture Overview

```
AIRA/
├── app/
│   ├── __init__.py           # Application factory (create_app), error handlers, request ID hooks
│   ├── config.py             # Environment configurations (Development, Production, Testing)
│   ├── extensions.py         # Extension singletons (SQLAlchemy, Migrate)
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py           # Reusable model mixins (TimestampMixin)
│   └── routes/
│       ├── __init__.py
│       └── health.py         # Versioned health check endpoint (/api/v1/health)
├── docs/
│   └── architecture-decisions/
│       ├── ADR-001-flask-application-factory.md
│       ├── ADR-002-mysql-sqlalchemy-database-strategy.md
│       ├── ADR-003-multi-user-data-isolation.md
│       └── ADR-004-future-memory-architecture.md
├── tests/
│   ├── conftest.py           # Test fixtures with isolated SQLite database
│   ├── unit/
│   │   └── test_config.py    # Configuration and connection URI tests
│   └── integration/
│       └── test_health.py    # Health endpoint, Request ID, and Error handling tests
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── requirements.txt          # Minimal Phase 1 dependencies
└── run.py                    # Application entry point
```

---

## Implemented vs. Future Capabilities

### Implemented in Phase 1
- **Flask Application Factory**: Clean separation of app creation and configuration.
- **Environment-Driven Configuration**: Strict fail-fast configuration for MySQL with zero silent SQLite fallback in development or production.
- **API Versioning**: Standard `/api/v1` namespace.
- **Health Check Endpoint**: `GET /api/v1/health` returning service status and version metadata.
- **Request ID Tracking**: Automatic generation and client propagation of `X-Request-ID` headers for request lifecycle tracing.
- **Standardized Error Handling**: Uniform JSON error envelopes for HTTP 400, 404, 405, and 500 without leaking stack traces or internal implementation details.
- **Database Foundation**: `Flask-SQLAlchemy` and `Flask-Migrate` singletons with `TimestampMixin`.
- **Isolated Testing Suite**: Pytest configuration running against isolated in-memory SQLite (`sqlite:///:memory:`).

### Deferred to Future Phases
- **Domain Database Models**: User, Company, ResearchReport, Watchlist, Conversation, Memory tables.
- **User Authentication**: JWT authentication, registration, login, and tenant access controls.
- **Multi-Agent Orchestration**: CrewAI research workflows and specialized agent roles.
- **LLM Reasoning**: Gemini API integration and structured prompt pipelines.
- **Vector Memory**: Supabase / PostgreSQL + `pgvector` semantic storage and RAG retrieval.
- **Financial Ingestion & Visualizations**: Market data feeds, scrapers, financial scorecards, and charts.

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
Copy `.env.example` to `.env` and configure your MySQL database credentials:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL details:
```ini
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://aira_user:aira_password@localhost:3306/aira_db
# Or specify individual parameters (MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD)
```

---

## Running the Application

Start the Flask development server:
```bash
python run.py
```

Verify the health check endpoint:
```bash
curl http://127.0.0.1:5000/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "AIRA",
  "version": "0.1.0"
}
```

---

## Running Tests

Run the automated test suite with pytest:
```bash
python -m pytest -v
```

All tests execute against an isolated in-memory SQLite database and never interact with your local MySQL database.
