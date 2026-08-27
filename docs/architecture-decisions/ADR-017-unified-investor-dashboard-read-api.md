# ADR-017: Unified Investor Dashboard & Read API Foundation

## Status
Accepted

## Context
As AIRA has grown through Phases 1 to 13, the system has accumulated powerful capabilities across portfolio valuations, watchlists, deterministic alerts, evidence-grounded research reports, multi-channel notifications, and scheduled monitoring.

A frontend web or mobile client attempting to render a comprehensive investor dashboard would previously need to execute 7 to 10 separate API requests (`/profile`, `/portfolio/snapshot`, `/watchlist`, `/alerts`, `/research/history`, `/notifications/preferences`, `/notifications/deliveries`, `/monitoring/status`). This causes:
1. Increased client latency and roundtrips.
2. Complex frontend state assembly and error handling.
3. Uncoordinated loading states on the user interface.

## Decision
1. **Dedicated Read-Model Orchestration Layer (`DashboardService`)**:
   - Created `DashboardService` which aggregates existing domain services (`PortfolioService`, `WatchlistService`, `AlertService`, `ResearchService`, `NotificationService`).
   - The service contains **zero duplicate calculation or detection logic** and is strictly read-only.
2. **Authenticated Unified Endpoints**:
   - `GET /api/v1/dashboard`: Full snapshot covering all 8 domain areas (User Profile, Portfolio, Watchlist, Alerts, Research History, Notifications, Monitoring, Portfolio Intelligence availability).
   - `GET /api/v1/dashboard/summary`: Lightweight summary for widgets/headers.
3. **Zero Expensive AI / Monitoring Invocations on GET**:
   - `GET /api/v1/dashboard` never executes CrewAI/Gemini agent workflows or triggers batch monitoring runs.
4. **Bounded Collections & Query Efficiency**:
   - Collections are bounded (top 5 holdings, top 5 watchlist items, recent 5 alerts, recent 5 research summaries) to prevent unbounded memory growth and high query latency.
5. **Multi-Tenant Scoping & Secret Privacy**:
   - Strict scoping to `g.current_user.id`.
   - Webhook secrets, provider credentials, SMTP keys, and private semantic memories are strictly omitted.
6. **Graceful Partial-Data Degradation**:
   - If an individual market quote fails, portfolio snapshot gracefully exposes data-quality states without crashing the entire dashboard.

## Consequences
- **Positive**: Single roundtrip for frontend rendering of the investor command center.
- **Positive**: Clean separation between granular domain APIs and read-optimized view models.
- **Positive**: Zero LLM involvement in deterministic calculations or dashboard aggregation.
- **Positive**: Backward compatibility preserved across all granular endpoints.
