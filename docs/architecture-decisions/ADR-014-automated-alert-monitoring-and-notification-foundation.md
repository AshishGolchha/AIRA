# ADR-014: Automated Alert Monitoring & Notification Foundation

## Status
Accepted

## Context
In Phase 10, we implemented deterministic, user-scoped alert detection across portfolio holdings and watchlists. However, evaluating alerts required manual HTTP calls (`POST /api/v1/alerts/check`). To support production operations, AIRA requires an automated monitoring orchestration layer capable of batch-checking eligible users with failure isolation, run history tracking, and a decoupled notification delivery abstraction.

## Decision
1. **Separation of Detection from Delivery**:
   - `AlertService` remains the sole authority on deterministic alert detection rules.
   - `MonitoringService` orchestrates scheduled execution across eligible users (`alerts_enabled = True`), handling batching, timing, and run tracking (`AlertMonitoringRun`).
   - `NotificationService` handles decoupled notification delivery via the `BaseNotificationProvider` interface.
2. **Failure Isolation**:
   - Batch monitoring processes each user in an isolated transaction block (`try ... except ... db.session.rollback()`).
   - If an external market quote fails or a database conflict occurs for User A, User A's failure is logged and recorded in `AlertMonitoringRun.users_failed`, allowing User B, User C, etc. to proceed uninterrupted.
3. **Notification Idempotency**:
   - `NotificationDelivery` maintains a `UNIQUE(alert_id, channel)` constraint.
   - A single alert cannot generate duplicate notification attempts across repeated monitoring runs.
   - Provider delivery failures record `status="failed"` with failure reasons, without deleting or corrupting the underlying `Alert`.
4. **Strict Multi-Tenant Security**:
   - Scheduled monitoring queries eligible user IDs directly from the database (`User.query.filter_by(alerts_enabled=True)`).
   - No client-controlled user IDs can trigger unauthorized batch monitoring.
   - Alerts and notification records strictly preserve `user_id` scoping.
5. **Decoupled Future Provider Path**:
   - `InAppNotificationProvider` serves as the initial default delivery channel.
   - Future channels (Email via SES/SendGrid, Mobile Push via FCM, Webhook, SMS) can be plugged into `NotificationService` without altering alert detection logic.

## Consequences
- **Positive**: Automated, resilient batch monitoring that can be driven by any scheduler (cron, systemd timer, Windows Task Scheduler, Celery).
- **Positive**: Complete failure isolation between users during batch runs.
- **Positive**: Strict notification idempotency preventing notification spam.
- **Positive**: Clean extension point for future external notification providers.
