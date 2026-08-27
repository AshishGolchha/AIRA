# ADR-013: Portfolio & Watchlist Alert Detection Foundation

## Status
Accepted

## Context
Investors tracking portfolios and watchlists require deterministic, timely awareness of critical events: severe daily price swings, major unrealized gains or losses across holdings, and data quality issues (such as missing market quotes). However, this alert detection must remain strictly grounded in verified facts, separate from notification delivery infrastructure, and safeguarded against mathematical hallucinations and alert spam.

## Decision
1. **Separation of Detection from Delivery**:
   - Detection is implemented as deterministic Python rule evaluations in `AlertService`.
   - Delivery infrastructure (push notifications, email, SMS, Celery, Redis, background worker daemons) is explicitly deferred to future phases.
   - Future scheduled monitoring or cron workers will invoke the exact same `AlertService.check_and_create_alerts(user_id)` method.
2. **Deterministic Alert Rules Engine**:
   - **Data Quality Alerts (`data_quality`)**: Triggered when holding quotes are unavailable without fabricating prices or treating missing data as losses.
   - **Gain / Loss Alerts (`portfolio_gain`, `portfolio_loss`)**: Triggered when holding unrealized gain/loss percentages breach configured thresholds (default ±10%, critical severity at -20%).
   - **Price Movement Alerts (`price_move`, `watchlist_move`)**: Triggered when daily price movement percentage breaches configured thresholds (default ±5%).
   - Zero LLM involvement in numerical rule evaluation.
3. **Duplicate Prevention & Idempotency**:
   - Before creating an alert, the engine verifies whether an active (non-dismissed) alert for the unique combination `(user_id, symbol, alert_type)` already exists.
   - Repeated check runs will not generate redundant duplicate alerts or cause alert explosion.
4. **Strict Multi-Tenant Isolation**:
   - All alert operations (check, list, get, mark as read, dismiss) strictly filter by `user_id = g.current_user.id` resolved exclusively from verified JWT tokens.
   - Client-provided `user_id` values in request payloads or query parameters are strictly ignored.
   - Cross-user alert access or manipulation returns `404 Not Found` to prevent ID enumeration.

## Consequences
- **Positive**: Reliable, deterministic, multi-tenant investment alerts with persistent read/dismiss tracking.
- **Positive**: Complete prevention of alert flooding through non-dismissed uniqueness checks.
- **Positive**: Clean foundation ready for future background worker/scheduler integration.
