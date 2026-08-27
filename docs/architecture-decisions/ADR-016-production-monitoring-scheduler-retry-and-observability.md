# ADR-016: Production-Grade Scheduled Monitoring, Retry & Observability Foundation

## Status
Accepted

## Context
In Phases 11 and 12, we developed automated alert detection, multi-channel notification delivery (In-App, Email, Webhooks), and preference filtering. To make this architecture fully production-ready for automated scheduling (via CLI, cron, or external cloud workers), the system requires:
1. Distributed concurrency locking to prevent overlapping execution cycles across multiple worker processes.
2. An automatic retry engine with exponential backoff for transient notification transport errors.
3. Observability and explicit lifecycle states (`completed`, `partial_failure`, `failed`).
4. A unified, scheduler-agnostic execution runner without introducing heavy message broker dependencies (Celery, Redis, RabbitMQ) prematurely.

## Decision
1. **Database-Backed Single-Run Concurrency Locking (`MonitoringLock`)**:
   - Implemented `monitoring_locks` table.
   - Any runner process acquires a lock before starting a batch cycle.
   - Stale locks automatically expire after `MONITORING_LOCK_TIMEOUT_SECONDS` (default 300s), ensuring transient crashes never cause deadlock.
2. **Scheduler-Agnostic Execution Entry Point (`MonitoringRunner`)**:
   - Provides a clean `run()` interface that checks feature flags, acquires the lock, executes batch monitoring, runs due notification retries, and safely releases the lock.
   - Callable via CLI (`python -m app.monitoring`), system cron, or future workers.
3. **Notification Failure Classification & Exponential Backoff**:
   - Errors are classified into **retryable** (timeouts, connection drops, HTTP 429, HTTP 5xx) vs **non-retryable** (SSRF blocks, invalid URLs, missing recipients, 4xx errors).
   - Exponential backoff delay calculation: `delay = min(base_delay * 2^(attempt - 1), max_delay)`.
   - Subsequent retry cycles reuse existing `NotificationDelivery` records (`attempt_count`, `next_retry_at`, `status`), strictly preserving the `UNIQUE(alert_id, channel)` idempotency invariant.
4. **Enhanced Run Lifecycle**:
   - Tracks metrics: `users_checked`, `users_succeeded`, `users_failed`, `alerts_generated`, `notifications_attempted`, `notifications_succeeded`, `notifications_failed`, and `duration_seconds`.
   - Sets status to `completed` on 100% success, `partial_failure` if isolated errors occurred, or `failed` if the entire run could not process any users.
5. **Observability & Operational Status API**:
   - `GET /api/v1/monitoring/status` exposes high-level health and latest run metrics without leaking user portfolios or provider secrets.

## Consequences
- **Positive**: Complete multi-process concurrency safety without external infrastructure.
- **Positive**: Transient network and provider outages recover automatically without creating duplicate notifications.
- **Positive**: Zero LLM involvement in numerical evaluation, locking, or retry decisions.
- **Positive**: Clean future migration path to distributed task workers (Celery/RQ) when scale necessitates.
