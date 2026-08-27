# ADR-018: Portfolio Intelligence Persistence and History

## Status
Accepted

## Context
In Phase 12, AIRA introduced the personalized portfolio and watchlist intelligence workflow (`POST /api/v1/portfolio/intelligence`) powered by CrewAI and Google Gemini. However, previously generated intelligence reports were ephemeral and not persisted into the relational database.

In Phase 14, the unified investor dashboard (`GET /api/v1/dashboard`) was established, but it was unable to show previously generated intelligence because no persisted history existed. Furthermore, users could not review past intelligence reports, compare their previous allocations against earlier AI analysis, or track historical risk discussions.

## Decision
1. **Persistent Domain Entity (`PortfolioIntelligenceRecord`)**:
   - Created the `portfolio_intelligence_records` table and SQLAlchemy model.
   - Preserves complete snapshot metadata at the exact time of generation: verified financial facts, portfolio holdings, watchlist priorities, user memories, risk assessments, opportunities, and source provenance.
2. **Snapshot Invariant**:
   - Historical intelligence records are immutable snapshots. If a user subsequently modifies or deletes holdings in their portfolio, historical intelligence reports remain intact and reflect the exact state of the portfolio when the report was generated.
3. **Strict Fact vs. AI Analysis Separation**:
   - Verified numerical values (cost basis, current prices, market valuations, gain/loss, concentration weights) and data source metadata are stored in structured `facts` and `sources` columns.
   - Qualitative reasoning and investment commentary produced by CrewAI/Gemini are stored separately (`summary`, `portfolio_overview`, `portfolio_risks`, `portfolio_opportunities`, `watchlist_priorities`, `recommended_research`).
4. **User-Scoped History API**:
   - `GET /api/v1/portfolio/intelligence/history`: Returns paginated lightweight summaries.
   - `GET /api/v1/portfolio/intelligence/history/<id>`: Returns full report by ID.
   - `DELETE /api/v1/portfolio/intelligence/history/<id>`: Deletes report owned by authenticated user.
   - Strict 404 response on cross-user access prevents user enumeration.
5. **Dashboard Read-Model Integration**:
   - `GET /api/v1/dashboard` reads the latest persisted record using single indexed query `WHERE user_id = :id ORDER BY created_at DESC LIMIT 1`.
   - Strictly read-only: Zero AI calls, zero external financial provider calls, and zero database writes during dashboard GET requests.
6. **Fail-Safe Integrity**:
   - If AI generation produces malformed output or fails schema validation, zero database records are created and transactions are safely rolled back.

## Consequences
- **Positive**: Complete audit trail and historical review of personalized portfolio recommendations.
- **Positive**: Dashboard displays latest intelligence instantly with 0ms LLM latency and zero token costs.
- **Positive**: Robust multi-tenant isolation and strict fact provenance.
- **Positive**: Backward compatibility preserved for all existing portfolio endpoints.
