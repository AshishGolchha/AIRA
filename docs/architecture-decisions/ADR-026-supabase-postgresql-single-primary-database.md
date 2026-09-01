# ADR-026: Supabase PostgreSQL as Single Primary Relational & Vector Database

## Status
Accepted (Supersedes ADR-002 and ADR-006 dual-database model)

## Context
In earlier architectural phases (ADR-002, ADR-006), AIRA operated a dual-database architecture:
1. MySQL was used as the primary transactional relational database (users, portfolios, research records, alerts, notifications).
2. Supabase PostgreSQL + `pgvector` was used for persistent semantic memory embeddings.

Maintaining two separate operational database engines introduced unnecessary architectural friction, multi-engine connection pooling overhead, duplicate deployment maintenance, and dual schema tracking.

## Decision
1. **Single Primary Database**: Supabase PostgreSQL is established as the single, authoritative database for the entire AIRA application.
2. **Relational Data Tier**: All relational models (users, user profiles, portfolios, watchlists, research records, intelligence records, alerts, notification preferences/endpoints/deliveries, monitoring runs/locks) are hosted in Supabase PostgreSQL and accessed via SQLAlchemy ORM using `psycopg2-binary`.
3. **Semantic Memory Tier**: Semantic investor memory (`user_memories` table with 768-dimensional Gemini embeddings and `match_user_memories` cosine similarity RPC) is natively co-located within the same Supabase database.
4. **Complete MySQL Decommissioning**: MySQL dependencies (`PyMySQL`), MySQL container services, and MySQL configuration variables are completely removed from the runtime.
5. **Authentication Invariants Preserved**: Application-level JWT authentication and integer `user_id` identifiers are strictly preserved.
6. **Testing Isolation**: Pytest test suites continue using in-memory SQLite (`sqlite:///:memory:`) for fast, isolated, deterministic execution.

## Consequences
- **Positive**:
  - Unified database architecture: One connection pool, one backup regime, one security perimeter.
  - Zero local database container dependencies required for cloud-native execution.
  - Native support for JSONB, HNSW vector indexes, and ACID transactional consistency across all relational models.
- **Trade-off**:
  - Requires network access to Supabase PostgreSQL or valid connection pooler credentials for live execution.
