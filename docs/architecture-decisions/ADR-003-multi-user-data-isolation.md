# ADR-003: Multi-User Data Isolation Strategy

## Status
Accepted

## Context
AIRA is designed as a multi-user platform where private investor preferences, watchlists, research history, customized theses, and memory must never leak across users. Relying purely on convention or ad-hoc query conditions invites tenant isolation vulnerabilities.

## Decision
Enforce a multi-tenant isolation pattern where user-scoped data is strictly accessed through authenticated user identity:
1. **Authenticated Context**: Every authenticated request resolves the user identity (`user_id`) from verified credentials/tokens.
2. **Mandatory User Scoping**: All queries accessing private resources must filter on `user_id`.
3. **Defense in Depth**: Isolation will be enforced at the application/query layer, verified via dedicated integration tests.

In Phase 1, the foundational infrastructure provides clean request context and base architecture to support this model without introducing premature authentication abstractions.

## Consequences
- **Positive**: Clear boundary preventing data leakage between user tenants.
- **Positive**: Architecture is prepared for seamless integration of JWT authentication and user-scoped data access in subsequent phases.
- **Trade-off**: Requires strict discipline in future domain queries to ensure tenant filtering is always present.
