# ADR-019: Modern Frontend Application Foundation (React + TypeScript + Vite + Tailwind CSS)

## Status
Accepted

## Context
Through Phase 15, the AIRA platform provided a robust, multi-tenant, autonomous investment intelligence backend supporting deterministic portfolio snapshots, watchlist priorities, automated alert telemetry, multi-agent AI research, multi-channel notifications, and persistent portfolio intelligence history.

To enable end investors and researchers to seamlessly interact with these capabilities, AIRA required a modern, accessible, high-performance web frontend application directory (`frontend/`) that integrates directly with the Flask backend while maintaining strict tenant isolation, dark-first luxury financial aesthetic, responsive design, and robust error handling.

## Decisions

### 1. Technology Architecture
- **Framework & Build**: React 18 with TypeScript and Vite for ultra-fast HMR and optimized production bundles (`dist/`).
- **Styling**: Tailwind CSS with custom theme extensions tailored for financial dashboards (deep `#090B10` background, subtle glow gradients, fine translucent glass surfaces with `-webkit-backdrop-filter`).
- **Routing**: React Router v6 with declarative `ProtectedRoute` authentication guards.
- **Icons**: Lucide React for consistent financial, telemetry, and AI iconography.

### 2. Centralized Typed API Client
- Implemented `frontend/src/lib/api.ts` encapsulating uniform error unwrapping, Bearer JWT token header injection, and tracing headers (`X-Request-ID`).
- Mapped all backend domains (Auth, Profile, Dashboard, Portfolio, Watchlist, Alerts, Intelligence, Research, Notifications, Monitoring) into strictly typed async namespaces.

### 3. State Management & Authentication
- Built `AuthContext` with automatic localStorage JWT token synchronization and server validation against `GET /api/v1/auth/me`.
- Built `ToastContext` providing non-intrusive, auto-dismissing visual feedback for all mutations.

### 4. Zero-Leak Dashboard Invariant
- Maintained the invariant that `GET /api/v1/dashboard` is strictly read-only.
- The dashboard visualizes the latest persisted portfolio intelligence report without triggering expensive or redundant LLM calls on page load. Intelligence synthesis is executed exclusively on-demand via the Intelligence workspace.

### 5. Design System & Component Primitives
- Developed accessible UI primitives: `Button`, `Card`, `GlassCard`, `Badge`, `StatusBadge`, `Input`, `Select`, `Modal`, `Tabs`, `Table`, `EmptyState`, `LoadingState`, `Skeleton`, `ErrorState`, `PageHeader`, `MetricCard`.
- Created responsive application shell (`AppLayout`, `Sidebar`, `Navbar`, `MobileNav`) with collapsible desktop navigation and touch-friendly mobile drawer.

## Consequences
- Single unified codebase where backend and frontend are clearly decoupled.
- Verified test suites across both layers: 179 Python pytest tests and 9 TypeScript Vitest component/integration tests passing.
