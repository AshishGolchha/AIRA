# ADR-002: MySQL + SQLAlchemy Database Strategy

## Status
Accepted

## Context
AIRA requires persistent storage for transactional application data (users, watchlists, research jobs, audit logs) and will later incorporate vector storage for semantic memory and RAG. A single database technology cannot optimally serve both structured relational transactions and large-scale vector similarity searches. Furthermore, test suites require rapid, isolated execution without polluting or requiring live MySQL databases.

## Decision
1. **Primary Transactional Database**: MySQL (via `PyMySQL` and `SQLAlchemy` / `Flask-SQLAlchemy`) is the dedicated relational store for all application data in development and production.
2. **Strict Configuration Enforcement**: Development and production environments do not silently fall back to SQLite. If MySQL connection variables or `DATABASE_URL` are missing, initialization fails immediately with an explicit configuration error.
3. **Test Suite Isolation**: The test suite explicitly uses in-memory SQLite (`sqlite:///:memory:` via `TestingConfig`). Tests never connect to or modify the development/production MySQL database.
4. **Schema Migrations**: Schema evolution will be handled via `Flask-Migrate` (Alembic).
5. **Future Vector Database**: Supabase / PostgreSQL + `pgvector` will be introduced in subsequent phases specifically for semantic memory and vector indexing, decoupled from MySQL.

## Consequences
- **Positive**: Clear separation between relational transactional state (MySQL) and isolated testing environments (in-memory SQLite).
- **Positive**: Strict fail-fast configuration prevents accidental data pollution or silent fallback to SQLite in production.
- **Trade-off**: Requires running a MySQL instance for local development.
