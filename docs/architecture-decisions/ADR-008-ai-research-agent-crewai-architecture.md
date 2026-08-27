# ADR-008: AI Research Agent & Multi-Agent Crew Architecture (CrewAI)

## Status
Accepted

## Context
AIRA aims to deliver personalized, verifiable investment intelligence. Rather than relying on a single monolithic prompt, complex investment synthesis requires specialized reasoning: factual data retrieval, fundamental quantitative analysis, competitive moat assessment, risk profiling, and personalized executive synthesis. Concurrently, AI agents must not bypass the existing financial data provider abstraction, must not fabricate sources, and must respect multi-tenant user memory isolation.

## Decision
1. **Agent Framework: CrewAI**:
   - Adopt CrewAI (`crewai`) as the sole agent framework for multi-agent reasoning.
   - Configure Google Gemini (`gemini/gemini-2.0-flash`) as the primary LLM backing agent execution.
2. **Three-Agent Sequential Pipeline**:
   - **Financial Data Researcher**: Uses CrewAI tools to query AIRA's existing `FinancialDataService` for real-time quotes, profiles, historical trends, fundamental financials, valuation metrics, and news.
   - **Investment Analyst**: Analyzes valuation multiples (P/E, P/B, EV/EBITDA), operational margins, balance sheet obligations, and competitive moat strengths.
   - **Research Synthesizer**: Produces a standardized JSON report (`ResearchReport`), tailoring conclusions to retrieved user memory preferences and citing verified source metadata.
3. **Single Source of Truth for Data Access**:
   - CrewAI tools wrap the existing `FinancialDataService` methods. Agents never call third-party APIs or `yfinance` directly.
4. **Tenant-Scoped Memory Personalization**:
   - User memory retrieval is strictly scoped to `g.current_user.id` resolved from verified JWT claims.
   - User investment preferences and strategy notes are injected as context into the research crew without polluting global financial knowledge.
5. **No Automatic Full-Report Writeback**:
   - Full research outputs are returned to the client rather than immediately dumped into vector memory, preventing memory saturation and noisy retrieval.

## Consequences
- **Positive**: Clear separation of concerns between data discovery, quantitative analysis, and synthesis.
- **Positive**: Strict tenant isolation on personal memory context.
- **Positive**: Verifiable citations attached to all financial facts.
- **Trade-off**: Multi-agent sequential execution introduces LLM token usage and latency; mitigated by lightweight tool delegation and focused agent prompts.
