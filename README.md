# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, and personalized portfolio tracking.

---

## Current Phase

**Phase 2 — Database Schema, Authentication & User Identity Foundation**

Phase 2 builds the user identity and multi-tenant isolation foundation:
- Domain models: `User` and `UserProfile` with a 1-to-1 relationship and UTC timestamp tracking.
- Stateless JWT authentication via `PyJWT` with configurable expiration.
- Secure password hashing using native `werkzeug.security` (scrypt/pbkdf2).
- Zero client-trust identity resolution via the `@auth_required` decorator (`g.current_user`).
- User-scoped profile management (`GET` and `PUT` `/api/v1/profile`) with whitelisted field updates.
- Centralized database migrations via `Flask-Migrate` / `Alembic`.
- Comprehensive automated tests with multi-tenant isolation verification.

> **Important Scope Clarification**:
> Phase 2 establishes user identity, authentication, and database foundation. It does **not** yet implement investment analysis, Gemini LLM reasoning, CrewAI multi-agent orchestration, or vector memory retrieval (Supabase/pgvector).

---

## Technology Stack

- **Runtime**: Python 3.10+
- **Web Framework**: Flask 3.x
- **Authentication & Security**: PyJWT, Werkzeug Security
- **ORM & Migrations**: SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Primary Database**: MySQL (via PyMySQL driver)
- **Testing**: Pytest (utilizing isolated in-memory SQLite)
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
│   │   └── user.py           # User & UserProfile SQLAlchemy models
│   └── routes/
│       ├── __init__.py
│       ├── auth.py           # Authentication routes (register, login, me)
│       ├── health.py         # Versioned health check endpoint (/api/v1/health)
│       └── profile.py        # User profile routes (get, update)
├── docs/
│   └── architecture-decisions/
│       ├── ADR-001-flask-application-factory.md
│       ├── ADR-002-mysql-sqlalchemy-database-strategy.md
│       ├── ADR-003-multi-user-data-isolation.md
│       ├── ADR-004-future-memory-architecture.md
│       └── ADR-005-jwt-authentication-strategy.md
├── migrations/               # Alembic database migration scripts
│   └── versions/
├── tests/
│   ├── conftest.py           # Test fixtures with isolated SQLite database
│   ├── unit/
│   │   └── test_config.py    # Configuration and connection URI tests
│   └── integration/
│       ├── test_auth.py      # Registration, login, auth context tests
│       ├── test_health.py    # Health endpoint, Request ID, and Error handling tests
│       └── test_profile.py   # Profile endpoints & critical multi-user isolation tests
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

Edit `.env` with your settings:
```ini
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://aira_user:aira_password@localhost:3306/aira_db
JWT_SECRET_KEY=your-secure-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES_SECONDS=86400
```

### 5. Run Database Migrations
```bash
flask db upgrade
```

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

All tests execute against an isolated in-memory SQLite database (`sqlite:///:memory:`) and never interact with your local MySQL database.
