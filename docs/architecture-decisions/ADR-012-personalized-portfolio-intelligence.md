# ADR-012: Personalized Portfolio & Watchlist Intelligence

## Status
Accepted

## Context
In Phase 8, we established the user investment universe foundation: personal watchlists, portfolio holdings ledger, and deterministic valuation snapshots. However, users need synthesis and actionable insights: answering questions about risk concentration, opportunities across holdings and watchlists, and prioritization aligned with their profile preferences, private semantic memories, and prior research history.

## Decision
1. **Orchestration Layer (`PortfolioIntelligenceService`)**:
   - Reuses existing specialized services (`PortfolioService`, `WatchlistService`, `FinancialDataService`, `MemoryService`, `ResearchService`) without duplicating domain logic.
   - Assembles a compact, pre-verified factual dataset containing portfolio snapshot valuations, concentration weights, watchlist items with latest quotes, and user personalization context.
2. **Deterministic Financial Math & Concentration Weights**:
   - All holding valuations (`market_value`, `cost_basis`, `unrealized_gain_loss`, `unrealized_gain_loss_percent`) and concentration weights (`(market_value / total_market_value) * 100`) are computed deterministically in Python using `Decimal`.
   - The LLM is never tasked with calculating numbers or portfolio weights.
   - If market quotes are temporarily unavailable, the position is marked as unavailable without fabricating placeholder or zero prices.
3. **CrewAI Sequential Intelligence Architecture**:
   - Reuses the 3-agent research pattern:
     - **Portfolio Researcher**: Reviews verified portfolio allocations, valuations, and watchlist facts.
     - **Investment Analyst**: Analyzes concentration risks, fundamental health, and opportunities grounded strictly in verified evidence.
     - **Personalized Research Synthesizer**: Connects facts with user preferences and private semantic memories into an actionable structured intelligence report.
4. **Strict Multi-Tenant Isolation**:
   - All inputs (holdings, watchlist, profile, memories, research history) are resolved strictly for `g.current_user.id` from verified JWT claims.
   - Client-provided `user_id` parameters are ignored.
5. **Safe Empty-State and Failure Resiliency**:
   - If the user has 0 holdings and 0 watchlist items, the service returns an informative report with setup guidance rather than crashing or hallucinating investments.
   - Malformed AI model outputs fail safely with a `RuntimeError` translating to a standardized 500 error envelope.

## Consequences
- **Positive**: Authenticated investors receive evidence-grounded, personalized portfolio and watchlist intelligence.
- **Positive**: Strict tenant isolation ensures zero cross-user memory or portfolio leakage.
- **Positive**: Deterministic calculations prevent mathematical hallucinations.
