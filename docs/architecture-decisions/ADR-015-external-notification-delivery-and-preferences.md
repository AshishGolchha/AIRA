# ADR-015: External Notification Delivery & User Preferences

## Status
Accepted

## Context
In Phase 11, we introduced `NotificationService`, `NotificationDelivery`, and `InAppNotificationProvider` to decouple alert detection from notification delivery. However, production users require granular preference controls (which channels to notify, minimum alert severity, enabled alert categories) as well as external delivery channels (Email and Webhooks). Because webhooks accept user-specified destination URLs, strict SSRF defenses are critical.

## Decision
1. **User Notification Preferences (`NotificationPreference`)**:
   - 1-to-1 relationship with `User`.
   - Stores channel toggles (`in_app_enabled`, `email_enabled`, `webhook_enabled`), `minimum_severity` (`info`, `warning`, `critical`), and optional `alert_types` filtering list.
   - Defaults are safe and backward compatible (`in_app_enabled=True`, `email_enabled=True`, `webhook_enabled=False`, `minimum_severity="info"`).
2. **Notification Endpoints (`NotificationEndpoint`)**:
   - Secure table for user-scoped webhook destination URLs and optional HMAC signing secrets (`secret_key`).
   - `to_dict()` never exposes `secret_key`.
3. **SSRF Protections on Webhook Delivery**:
   - Requires HTTPS URLs.
   - Validates hostnames and resolves IP addresses against blocked ranges: loopback (`127.0.0.0/8`, `::1`), private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), cloud instance metadata endpoints (`169.254.169.254`), and dangerous protocols (`file:`, `javascript:`, `data:`, `ftp:`).
   - Enforces a strict 5.0-second network timeout and isolates errors.
4. **HMAC SHA-256 Webhook Signing**:
   - If `secret_key` is configured on an endpoint, outbound HTTP POST requests include an `X-AIRA-Signature: sha256=<hex>` header.
5. **Decoupled Email Provider (`EmailNotificationProvider`)**:
   - Formats alert subjects and structured bodies with verified facts, sources, and severity metadata.
   - Provider failures or absent API keys fail gracefully and record `status="failed"` without halting alert creation or batch monitoring.
6. **Multi-Channel Dispatch & Idempotency in `NotificationService`**:
   - Evaluates user preferences and filters before attempting delivery.
   - Enforces database-level idempotency via `UNIQUE(alert_id, channel)`.
   - Repeated scheduled monitoring runs on unchanged data never spam external endpoints.
7. **Strict Multi-Tenant Isolation**:
   - Preferences and endpoints are queried and updated exclusively via `g.current_user.id` or server-side DB relationships.
   - Cross-user endpoint access returns `404 Not Found`.

## Consequences
- **Positive**: Full user autonomy over notification routing, alert type filtering, and severity thresholds.
- **Positive**: Extensible provider architecture ready for future channels (Push, SMS, Slack).
- **Positive**: Strong SSRF defenses preventing cloud metadata theft or internal network port scans.
- **Positive**: Zero LLM involvement in numerical alerts or notification filtering.
