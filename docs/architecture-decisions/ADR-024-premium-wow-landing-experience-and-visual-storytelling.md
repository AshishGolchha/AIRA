# ADR-024: Premium WOW Landing Experience & Visual Product Story

## Status
Accepted

## Context
Following the baseline public landing page and SEO implementation in Phase 20A, the public homepage required a substantial visual storytelling and interactive upgrade to deliver a genuine "WOW" experience. The page needed to move beyond card-grid layouts to visually demonstrate AIRA as an autonomous investment research intelligence platform.

Key goals:
1. **Interactive Hero Intelligence Engine**: Transform the hero centerpiece into a multi-ticker (`$NVDA`, `$AAPL`, `$MSFT`) live simulation showing streaming SEC ingestion, autonomous multi-agent reasoning, and grounded thesis synthesis.
2. **Visual Architectural Differentiator**: Provide a visual circuit diagram contrasting the Autonomous AI Tier (qualitative moat and thesis reasoning) with the Deterministic Rule Tier (mathematical calculations, threshold rules, and retry-safe webhooks).
3. **Multi-Agent Deliberation Visualizer**: Showcase how specialized CrewAI agents (Senior Equity Analyst, Valuation Specialist, Macro Risk Officer) debate and synthesize evidence-backed consensus.
4. **Elimination of Card Grid Fatigue**: Implement diverse visual compositions including split-screen before/after lenses, terminal view mode toggling, and interactive ticker inspection.
5. **Zero External Overhead & Free Technical SEO**: Build purely with React 18 + Tailwind CSS + Lucide icons, invoking zero backend or AI API requests on initial load while preserving standard JSON-LD structured data, Open Graph tags, robots.txt, and sitemap.xml.

## Decision

### 1. Visual Design Architecture
- **Hero Intelligence Engine (`HeroIntelligenceEngine.tsx`)**: Interactive 3-column live engine simulator allowing visitors to switch between real company scenarios and inspect raw signals, active agent findings, and grounded thesis outputs.
- **Architecture Circuit (`ArchitectureCircuit.tsx`)**: Interactive 3-way circuit visualizer illustrating why mathematical portfolio valuation and alert thresholds operate on deterministic Python/SQL engines while qualitative thesis reasoning runs on multi-agent AI.
- **Multi-Agent Deliberation (`MultiAgentDebateVisual.tsx`)**: Interactive debate round inspector showing how multiple agents challenge assumptions and ground conclusions directly in cited SEC 10-Q disclosures.
- **Console Mode Toggle (`Landing.tsx`)**: The 6-stage lifecycle console now supports toggling between formatted Markdown synthesis and structured JSON payloads.

### 2. Styling System & Animation
- Extended `tailwind.config.js` with subtle custom keyframe animations: `pulse-slow`, `scanline`, `shimmer`, `float`, and `data-pulse`.
- Added grid pattern, radial lighting, scanline overlays, and strict `@media (prefers-reduced-motion: reduce)` accessibility overrides in `index.css`.

## Consequences

### Positive
- The homepage creates an immediate visual impact, communicating what AIRA is, how multi-agent research operates, and why deterministic calculation separation prevents hallucination.
- Rich interactivity with zero runtime token cost or backend overhead on public visits.
- All 195 backend tests, 28 Vitest unit/component tests across 12 suites, and 6 Playwright E2E browser flows pass.

### Considerations
- The interactive simulators use deterministic, illustrative scenario data to ensure sub-millisecond client rendering without external API dependencies.
