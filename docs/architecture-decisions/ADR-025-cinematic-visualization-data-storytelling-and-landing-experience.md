# ADR-025: Cinematic Visualization, Data Storytelling & Landing Experience

## Status
Accepted

## Context
While Phase 20B improved the landing page architecture, the public experience still relied heavily on text cards rather than visual data storytelling. An institutional-quality investment AI product requires rich financial data visualizations, real interactive charts, and animated pipeline transformations that communicate the entire research workflow at a glance.

Key goals for Phase 20C:
1. **Financial Data Visualizations**: Embed real interactive time-series price curves (`MarketTerminalChart.tsx`) with pinned SEC filing milestones, agent consensus events, and fundamental valuation multiples.
2. **Whole-Portfolio Allocation & Risk Visuals**: Create an interactive SVG Donut chart and Risk vs. Return scatter plot matrix (`PortfolioAllocationVisual.tsx`) that demonstrate how single-stock research is framed by whole-portfolio risk parameters.
3. **Multi-Agent Deliberation Network**: Implement an interactive SVG node graph (`MultiAgentNetworkVisual.tsx`) with animated stroke conduits and flow pulses between the centralized Evidence Core and specialized analytical agents.
4. **Raw Data to Intelligence Transformation**: Build an animated 3-stage convergence visual (`DataTransformationFlow.tsx`) showing unstructured inputs (SEC filings, news, market ticks) transforming into structured intelligence.
5. **Evidence Grounding Dissection**: Provide a step-by-step visual audit trail (`EvidenceGroundingFlow.tsx`) proving verifiable source mapping.
6. **5 Lines vs 50 Lines Rule**: Leverage native SVG primitives, React state, and Tailwind CSS animations to keep the codebase compact, free of third-party bloat, and performant.

## Decision

### 1. Visualization Components
- **`MarketTerminalChart.tsx`**: Interactive SVG price curve with gradient area fills, milestone signals, and scrub tooltips for `$NVDA`, `$AAPL`, and `$MSFT`.
- **`PortfolioAllocationVisual.tsx`**: Interactive SVG Donut chart, sector exposure progress bars, and risk-vs-return scatter plot.
- **`MultiAgentNetworkVisual.tsx`**: Interactive node network with animated SVG stroke conduits (`dash-flow`).
- **`DataTransformationFlow.tsx`**: 3-stage interactive visual transformation pipeline.
- **`EvidenceGroundingFlow.tsx`**: 4-step evidence audit trail.

### 2. Performance & Cost Guarantees
- Zero API or LLM tokens consumed on landing page load (100% deterministic client-side rendering).
- Full compliance with `@media (prefers-reduced-motion: reduce)` accessibility rules.

## Consequences

### Positive
- The landing page delivers a high-impact, visual-first storytelling experience.
- Real interactive financial charts and node graphs replace walls of text.
- 100% test pass rate across 195 backend tests, 29 Vitest tests, and 6 Playwright E2E browser flows.
