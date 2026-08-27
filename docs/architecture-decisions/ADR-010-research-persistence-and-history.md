# ADR-010: Research Persistence and User Research History

## Status
Accepted

## Context
In previous phases (Phases 5 and 6), AI research reports were generated on-demand via `POST /api/v1/research/analyze` and returned directly in the response payload. However, completed research analyses were not stored. Users need the ability to retrieve their prior research reports, inspect past findings, and track their research history over time without incurring redundant LLM or external financial API calls.

## Decision
1. **Relational Storage in MySQL (`research_records`)**:
   - Store completed research reports in a relational MySQL table `research_records` managed via SQLAlchemy and Flask-Migrate.
   - Maintain the Phase 6 strict separation of verified ground-truth `facts` and `sources` (stored as JSON) from AI analytical interpretations (`fundamentals`, `valuation`, `market_context`, `risks`, `opportunities`) and personalized `user_context`.
2. **Strict Multi-Tenant Isolation**:
   - Every `ResearchRecord` is linked to `users.id` with `ondelete="CASCADE"`.
   - All history listing, single report lookups, and deletions are scoped strictly to `user_id = g.current_user.id` resolved from verified JWT claims.
   - Client-provided `user_id` parameters are never trusted. Cross-user lookups return 404 Not Found to eliminate user ID enumeration.
3. **Failure Safety**:
   - Persistence occurs only after a `ResearchReport` has been successfully produced and validated.
   - Incomplete, malformed, or failed research workflows persist zero records.
4. **Lightweight History Summaries**:
   - `GET /api/v1/research/history` returns lightweight summaries (`id`, `company`, `symbol`, `query`, `summary`, `created_at`) with bounded pagination (`page`, `limit` up to 100), avoiding large JSON payloads during list requests.
   - `GET /api/v1/research/history/<id>` returns the complete report.
5. **Separation from Vector Memory**:
   - Research history records are separate from long-term semantic vector memories (Supabase `pgvector`). Research reports are not automatically converted into user preferences or semantic embeddings.

## Consequences
- **Positive**: Authenticated users can review, audit, and delete their previous investment analyses.
- **Positive**: Exact evidence, verified facts, and sources are preserved without re-generation or data mutation.
- **Positive**: Strict tenant isolation prevents unauthorized cross-user research exposure.
