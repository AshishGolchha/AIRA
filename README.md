# AIRA — Autonomous Investment Research Agent

## Project Vision

AIRA (Autonomous Investment Research Agent) is a multi-user AI investment research intelligence platform designed to assist investors with autonomous company analysis, financial synthesis, competitive intelligence, evidence verification, risk profiling, and personalized portfolio tracking.

---

## Current Phase

**Phase 3 — Persistent User Memory Foundation**

Phase 3 implements the persistent user-specific memory infrastructure using Supabase PostgreSQL + `pgvector` and Google Gemini vector embeddings (`text-embedding-004`):
- **User Memory Tier**: Long-term semantic memory storage with HNSW vector indexing.
- **Strict User Isolation**: All vector searches (`match_user_memories` RPC) and CRUD operations strictly enforce `WHERE user_id = g.current_user.id`.
- **Vector Embeddings**: 768-dimensional dense vectors generated via `EmbeddingService` wrapping `google-genai`.
- **Memory Management API**: `/api/v1/memory` endpoints for creating, listing, semantically searching, and deleting memories.
- **Exact Duplicate Prevention**: Prevents duplicate memory spam per user.
- **Dual Database Architecture**: MySQL maintains relational user identity and profiles; Supabase manages high-dimensional vector memory.

> **Important Scope Clarification**:
> Phase 3 implements persistent memory *infrastructure*. It does **not** yet implement CrewAI multi-agent research orchestration, automated conversation memory extraction, financial data ingestion, or company/global knowledge memory.

---

## Technology Stack

- **Runtime**: Python 3.10+
- **Web Framework**: Flask 3.x
- **Authentication & Security**: PyJWT, Werkzeug Security
- **Relational Database & Migrations**: MySQL, SQLAlchemy, Flask-SQLAlchemy, Flask-Migrate (Alembic)
- **Vector Database**: Supabase PostgreSQL + `pgvector`
- **Embeddings**: Google Gemini API (`text-embedding-004`, 768 dimensions)
- **Testing**: Pytest (isolated in-memory SQLite + mock vector services)
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
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes (register, login, me)
│   │   ├── health.py         # Versioned health check endpoint (/api/v1/health)
│   │   ├── memory.py         # User memory routes (create, list, search, delete)
│   │   └── profile.py        # User profile routes (get, update)
│   └── services/
│       ├── __init__.py
│       ├── embedding_service.py # Gemini text-embedding-004 provider
│       └── memory_service.py    # User-scoped semantic memory service
├── docs/
│   └── architecture-decisions/
│       ├── ADR-001-flask-application-factory.md
│       ├── ADR-002-mysql-sqlalchemy-database-strategy.md
│       ├── ADR-003-multi-user-data-isolation.md
│       ├── ADR-004-future-memory-architecture.md
│       ├── ADR-005-jwt-authentication-strategy.md
│       └── ADR-006-persistent-user-memory-supabase-pgvector.md
├── migrations/               # MySQL Alembic database migration scripts
│   └── versions/
│       └── 0001_create_users_and_user_profiles.py
├── supabase/                 # Supabase pgvector schema and migration scripts
│   └── migrations/
│       └── 001_create_user_memories.sql
├── tests/
│   ├── conftest.py           # Test fixtures with isolated SQLite database
│   ├── unit/
│   │   ├── test_config.py    # Configuration and connection URI tests
│   │   └── test_memory_service.py # Unit tests for memory and embedding services
│   └── integration/
│       ├── test_auth.py      # Registration, login, auth context tests
│       ├── test_health.py    # Health endpoint, Request ID, and Error handling tests
│       ├── test_memory.py    # Memory CRUD, vector search, and isolation tests
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
| `POST` | `/api/v1/memory` | Yes (`Bearer <token>`) | Store a new user memory and vector embedding |
| `GET` | `/api/v1/memory` | Yes (`Bearer <token>`) | List recent memories for authenticated user |
| `GET` | `/api/v1/memory/search` | Yes (`Bearer <token>`) | Semantic vector search (`?q=...&limit=...`) |
| `DELETE` | `/api/v1/memory/<id>` | Yes (`Bearer <token>`) | Delete a memory owned by authenticated user |

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

# Gemini API (Embeddings)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_EMBEDDING_MODEL=text-embedding-004
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

All 37 automated tests run deterministically against an isolated in-memory SQLite database (`sqlite:///:memory:`) and mock vector services.
