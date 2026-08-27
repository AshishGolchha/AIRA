# ADR-011: User Watchlist & Portfolio Foundation

## Status
Accepted

## Context
AIRA requires a user-isolated investment universe foundation enabling investors to curate personal watchlists and track their actual investment holdings (quantities, average cost bases, and notes). Users also need read-only calculated portfolio valuations (market values, cost bases, unrealized gain/loss amounts, and gain/loss percentages) evaluated against real-time market data.

## Decision
1. **Relational Models (`WatchlistItem` and `PortfolioHolding`)**:
   - Persist watchlists in MySQL `watchlist_items` and holdings in `portfolio_holdings` using SQLAlchemy and Flask-Migrate.
   - Enforce single-position-per-symbol per user via unique database constraints `uq_watchlist_user_symbol` (`UNIQUE(user_id, symbol)`) and `uq_portfolio_user_symbol` (`UNIQUE(user_id, symbol)`).
   - Normalize ticker symbols to uppercase before validation, lookup, and persistence.
2. **Precise Decimal Handling for Financial Holdings**:
   - Use `db.Numeric(18, 6)` for fractional quantities and `db.Numeric(18, 4)` for average cost.
   - Perform all cost-basis, market-value, and gain/loss arithmetic in Python using `Decimal` rather than floating-point math to prevent financial precision issues.
3. **Deterministic Portfolio Valuation (Zero LLM Involvement)**:
   - Portfolio snapshot calculations are strictly deterministic Python calculations using real-time quotes retrieved from `FinancialDataService`.
   - Never involve LLM or generative models in numeric portfolio calculations.
   - Zero-cost holdings or empty portfolios safely return `null` for gain/loss percentage rather than triggering division-by-zero errors.
   - If market quotes are temporarily unavailable, the position is clearly marked without fabricating placeholder or zero prices.
4. **Strict Multi-Tenant Isolation**:
   - Watchlist and portfolio endpoints require JWT authentication (`@auth_required`).
   - All CRUD operations filter strictly by `WHERE id = :id AND user_id = g.current_user.id`.
   - Client-provided `user_id` fields are rejected or ignored; authorization is derived exclusively from verified JWT tokens.
   - Cross-user lookups return `404 Not Found` to prevent ID enumeration.
5. **Separation from Trading & Transactions**:
   - Phase 8 establishes a holdings ledger and watchlist foundation. Broker integration, transaction ledgers, automated trading, and order execution are out of scope.

## Consequences
- **Positive**: Authenticated investors can curate watchlists, track portfolio positions, and view instantaneous valuations.
- **Positive**: Strict database-level and application-level isolation prevents cross-tenant data leakage.
- **Positive**: Deterministic Decimal arithmetic eliminates rounding errors and hallucinations in financial reporting.
