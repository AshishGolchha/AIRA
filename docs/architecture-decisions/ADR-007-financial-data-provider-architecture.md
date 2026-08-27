# ADR-007: Financial Data Provider Layer and Evidence Tracking Architecture

## Status
Accepted

## Context
AIRA requires reliable market quotes, company profiles, historical prices, fundamental financial statements, valuation metrics, and business news to power future autonomous research agents (Phase 5 CrewAI). Direct coupling between routes/agents and specific third-party financial APIs creates vendor lock-in, increases vulnerability to API schema changes, and complicates testing. Furthermore, autonomous financial intelligence requires that all externally retrieved data points carry verifiable source metadata so that AI agents can cite provenance.

## Decision
1. **Provider Abstraction (`BaseFinancialProvider`)**:
   - Establish an abstract provider contract (`get_company_profile`, `get_quote`, `get_historical_prices`, `get_financials`, `get_key_metrics`, `get_company_news`, `resolve_symbol`).
   - Implement `YFinanceProvider` utilizing `yfinance` to retrieve real-world market intelligence without requiring paid API infrastructure.
2. **Normalized Data Models with Source Metadata**:
   - Model research data into typed Python dataclasses (`CompanyProfile`, `MarketQuote`, `HistoricalPrices`, `FinancialStatement`, `KeyMetrics`, `NewsArticle`).
   - Standardize `SourceMetadata` (`provider`, `source_url`, `retrieved_at`, `data_type`, `symbol`) attached to every entity for transparent evidence tracking.
3. **Service Layer & In-Memory TTL Caching**:
   - `FinancialDataService` validates stock ticker symbols and provides lightweight in-process TTL caching (60s for market quotes, 300s for profiles/financials/metrics) to eliminate redundant API requests and prevent rate-limiting.
4. **Separation of Global Market Data vs. Private User Memory**:
   - Financial market data is global and shared across users.
   - User-specific investment preferences, risk tolerance, and personalized research history remain strictly isolated in MySQL and Supabase `pgvector`.
5. **Deterministic Testing Strategy**:
   - Normal automated tests mock the provider layer to maintain fast, deterministic, and 100% offline execution.

## Consequences
- **Positive**: Seamless integration path for Phase 5 CrewAI research agents.
- **Positive**: Zero paid infrastructure required during development.
- **Positive**: Strict data provenance enables verifiable, citation-backed AI research.
- **Trade-off**: `yfinance` relies on Yahoo Finance endpoints; provider errors and schema drift must be handled defensively by the provider layer.
