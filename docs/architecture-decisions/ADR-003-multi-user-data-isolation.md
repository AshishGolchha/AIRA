# ADR-003: Multi-User Data Isolation Strategy

## Status
Accepted

## Context
AIRA is designed as a multi-user platform where private investor preferences, watchlists, research history, customized theses, and memory must never leak across users. Relying purely on convention or ad-hoc query conditions invites tenant isolation vulnerabilities.

## Decision
Enforce a multi-tenant isolation pattern where user-scoped data is strictly accessed through authenticated user identity:
1. **Authenticated Context**: Every protected request verifies the bearer JWT token and resolves `g.current_user`.
2. **Zero Client Trust for Identity**: No endpoint accepts a client-provided `user_id` or `owner_id` (via URL parameter or JSON body) to determine data ownership. All operations are strictly bounded by `g.current_user`.
3. **Database-Level Enforced Isolation**: Models (such as `UserProfile`) enforce strict foreign keys to `users.id` with unique constraints. Queries access user-owned data directly through the authenticated relationship (e.g. `g.current_user.profile`).
4. **Defense in Depth**: Isolation is verified directly at the API/query boundary via automated multi-user integration tests.

## Consequences
- **Positive**: Complete prevention of IDOR (Insecure Direct Object Reference) vulnerabilities.
- **Positive**: Strict identity boundary established for future user-specific memory, research history, and watchlists.
- **Positive**: User A's private data is fundamentally inaccessible to User B.
