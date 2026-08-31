# ADR-023: Public Landing Page, Product Story, WOW Factor & Technical SEO

## Status
Accepted

## Context
Prior to Phase 20A, the root route (`/`) in the AIRA single-page application redirected immediately into the authenticated shell or the login screen. While functional for existing authenticated users, this created a friction point for first-time visitors and prospective users who needed to understand what AIRA is, how multi-agent research operates, why deterministic calculations prevent hallucination, and how personalized portfolio intelligence works.

Key requirements for the public web presence:
1. **Public Landing Page**: Transforming `/` into an informative public landing page.
2. **WOW Factor & Product Story**: An interactive "AIRA Intelligence Console" showcasing how data flows from discovery to multi-agent synthesis, portfolio weighting, deterministic telemetry, and vector memory.
3. **No Financial Overpromising**: Clean, honest positioning as an autonomous investment research intelligence and decision-support platform (no guaranteed returns, no fake trading bot claims, no fake social proof).
4. **Preserved App Architecture**: Existing protected application routes (`/app/*`) and authentication endpoints (`/login`, `/register`) remain isolated and guarded.
5. **Zero API Overhead on Load**: The landing page is completely static and client-rendered, preventing unnecessary backend or AI provider costs on public visits.
6. **Free Technical SEO**: Comprehensive semantic HTML, JSON-LD structured schema (`WebApplication` / `FinanceApplication`), Open Graph metadata, Twitter cards, `robots.txt`, and `sitemap.xml` without paid SEO subscriptions.

## Decision

### 1. Route Topology
- `/`: Public landing page (`Landing.tsx`). If a visitor is already authenticated, the header and hero CTAs dynamically render "Open Dashboard" linking to `/app/dashboard`.
- `/login` & `/register`: Public authentication views.
- `/app/*`: Protected application shell guarded by `ProtectedRoute` (`/app/dashboard`, `/app/portfolio`, `/app/watchlist`, `/app/alerts`, `/app/intelligence`, `/app/research`, `/app/notifications`, `/app/settings`). Direct unauthenticated visits to `/app/*` automatically redirect to `/login`.

### 2. Information Architecture
The landing page is organized into a cohesive, top-down story:
1. **Hero Section**: Eyebrow badge, primary H1 headline (*"Your Investment Research, Running on Autonomous Intelligence"*), supporting narrative, and primary/secondary CTAs.
2. **Trust & Capability Strip**: Highlighting multi-agent reasoning, real-time portfolio weights, deterministic telemetry, evidence grounding, vector memory (pgvector), and multi-tenant isolation.
3. **Interactive Intelligence Console (WOW Centerpiece)**: 6-stage interactive simulator allowing visitors to inspect sample outputs for Discovery, Valuation, Multi-Agent Consensus, Personalization, Telemetry, and Vector Memory.
4. **The Fragmentation Problem**: Contrasting traditional multi-tab research with AIRA's continuous intelligence layer.
5. **How AIRA Works**: 6-step lifecycle (01 Discover → 02 Ingest → 03 Synthesize → 04 Contextualize → 05 Monitor → 06 Retain).
6. **Core Capabilities Grid**: Deep dives into Company Research, Portfolio Intelligence, Watchlists, Deterministic Alerts, Memory, and Personalization.
7. **Deterministic Rule Separation**: Explaining the mathematical certainty of separating deterministic calculation rules from generative AI reasoning.
8. **Final CTA & Footer**: Links to register/sign in and explicit regulatory/financial disclaimer.

### 3. Technical SEO & Crawlability
- `index.html`: Open Graph tags, Twitter card tags, canonical URL, and JSON-LD schema describing software features and free pricing.
- `public/robots.txt`: Grants crawler access to `/`, `/login`, and `/register` while disallowing private `/app/` and `/api/` paths.
- `public/sitemap.xml`: XML sitemap declaring public URLs with change frequency and priority metadata.
- `public/og-image.svg`: Open Graph preview card.

## Consequences

### Positive
- Prospective users immediately understand AIRA's value proposition and multi-agent architecture within seconds of visiting `/`.
- Interactive console enables hands-on preview of AIRA's synthesis pipeline without incurring live LLM tokens.
- Technical SEO allows search engine indexing of AIRA's public research intelligence capabilities.
- Full backward compatibility: all 195 backend tests, 26 frontend Vitest tests, and 6 Playwright E2E browser flows pass.

### Considerations
- The SPA remains client-rendered with Vite. Future phases can implement SSG/SSR (e.g. Next.js or Astro) if deeper server-side HTML prerendering is required.
