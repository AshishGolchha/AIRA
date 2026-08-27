# ADR-006: Persistent User Memory with Supabase & pgvector

## Status
Accepted

## Context
AIRA requires long-term semantic memory for each investor to enable personalized research, persistent preference retention, and context injection across conversations. Relational databases like MySQL are optimized for transactional integrity (users, profiles, watchlists) but lack native, high-performance vector indexing and similarity search. Concurrently, memory operations must be strictly isolated per user so that investor data never leaks across tenant boundaries.

## Decision
1. **Dual Database Architecture**:
   - **MySQL**: Retains ownership of transactional data (users, user profiles, authentication credentials).
   - **Supabase PostgreSQL + `pgvector`**: Dedicated store for persistent semantic memory records and embeddings (`user_memories`).
2. **Vector Embeddings**:
   - Utilize Google Gemini `text-embedding-004` to generate 768-dimensional dense float vectors for user memories and search queries.
3. **User Isolation & Scoped Retrieval**:
   - Every memory record stores the canonical MySQL `user_id`.
   - Vector similarity search is executed via the `match_user_memories` RPC function, enforcing `WHERE user_id = p_user_id` at the database query level before returning top-k matches.
4. **Lightweight Extensibility**:
   - Supports memory categorization (`memory_type`), importance scoring (`importance`), and flexible key-value JSON metadata (`metadata`).
   - Implements exact-duplicate prevention to avoid repetitive memory records.

## Consequences
- **Positive**: Clean separation between structured transactional state and high-dimensional semantic search.
- **Positive**: Hard database-level tenant isolation prevents cross-user semantic leakage.
- **Positive**: Native HNSW cosine similarity search provides sub-millisecond retrieval.
- **Trade-off**: Requires managing connection credentials for both MySQL and Supabase services.
