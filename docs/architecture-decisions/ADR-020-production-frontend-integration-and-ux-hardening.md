# ADR-020: Production Frontend Integration, UX Hardening & End-to-End Validation

## Status
Accepted (Phase 17)

## Context
Following the completion of the foundation frontend architecture (Phase 16), the application required comprehensive UX hardening, strict synchronization with existing Flask backend API contracts, enhanced authentication lifecycle handling, robust state persistence, zero-stale state guarantees across all domain pages, and expanded test coverage.

## Architectural Decisions

### 1. Centralized Error Handling & Cross-Domain Unauthorized Dispatches
- **Problem**: Stale authentication tokens or 401 Unauthorized responses could leave the UI in an inconsistent state or trapped in infinite loading loops.
- **Decision**: Enhanced `api.ts` to clear authentication credentials and dispatch a decoupled `window.dispatchEvent(new CustomEvent('aira:unauthorized'))`. `AuthContext` listens to this event to immediately reset user state and redirect unauthenticated routes gracefully.

### 2. Zero-Stale State Architecture & Immediate Mutation Feedback
- **Problem**: Modifying resources (adding/editing/deleting portfolio positions, watchlist entries, alert thresholds, webhook endpoints) risked showing stale data or required manual page refreshes.
- **Decision**: All mutations strictly execute sequential invalidation cycles:
  1. Trigger backend mutation API with active submission states (`isSubmitting(true)`).
  2. Emit contextual toast notifications.
  3. Close modal dialogs.
  4. Immediately trigger domain query refresh to guarantee deterministic synchronization with database models.

### 3. Read-Only Dashboard Invariant
- **Decision**: The Unified Dashboard consumes `GET /api/v1/dashboard` as an aggregated read-only snapshot. No expensive AI multi-agent synthesis workflows are initiated on page load. Users can trigger AI syntheses explicitly from the Intelligence and Research workspaces.

### 4. Deterministic Telemetry Dual Coding & Accessibility
- **Decision**: All critical domain metrics (gains/losses, alert severity levels, priority ranks) use dual coding (color + iconography + semantic badges + ARIA labels) ensuring complete accessibility across desktop, tablet, and mobile displays.

### 5. Frontend Test Suite Architecture
- **Decision**: Built complete unit and integration test coverage across all pages (`Dashboard`, `Portfolio`, `Watchlist`, `Alerts`, `Intelligence`, `Research`, `Notifications`, `Settings`, `Navigation`, `Auth`, `ProtectedRoute`) using Vitest and React Testing Library with mocked API endpoints.

## Consequences
- **Positive**:
  - Genuinely responsive, accessible, and resilient production interface.
  - Zero-drift between backend response envelopes and frontend TypeScript interfaces.
  - Complete test coverage across 11 test suites (23 test cases).
  - 100% backward compatibility preserved with all existing backend services, models, migrations, and CLI workflows.
