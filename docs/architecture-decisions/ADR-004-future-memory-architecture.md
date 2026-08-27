# ADR-004: Future Memory Architecture

## Status
Accepted

## Context
AI-driven investment research requires contextual intelligence across three distinct scopes: global financial facts, historical company analysis, and personalized user investment criteria. Conflating these layers leads to memory corruption, loss of privacy, and suboptimal LLM reasoning.

## Decision
Establish a conceptual tri-tier memory architecture to be implemented in dedicated future phases:
1. **Global Knowledge**: Shared financial data, macroeconomic indicators, market terminology, and generalized investment models. Accessible across all users.
2. **Company Knowledge**: Persistent, aggregated research and fundamentals concerning specific securities/companies (e.g., historical earnings calls, competitive analyses, regulatory filings).
3. **User Memory**: Private user preferences, risk profiles, past queries, active investment theses, and conversational history. Strictly scoped by `user_id`.

**Phase 1 Scope Boundary**:
The memory engine (embeddings, vector retrieval, pgvector indexing, memory consolidation, RAG pipelines) is intentionally deferred to later phases. No fake memory or placeholder vector stores are implemented in Phase 1.

## Consequences
- **Positive**: Clean mental model for multi-agent retrieval without premature complexity.
- **Positive**: Zero dead code or unneeded vector dependencies in Phase 1.
- **Trade-off**: Memory retrieval must be developed and validated in a dedicated subsequent phase.
