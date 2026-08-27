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

**Phase 3 Implementation**:
Phase 3 establishes the foundation for the **User Memory** tier using Supabase PostgreSQL + `pgvector` and Gemini embeddings (`text-embedding-004`). Memories are strictly scoped to `user_id`. Company Knowledge and Global Knowledge remain deferred to subsequent phases.

## Consequences
- **Positive**: Clean mental model for multi-agent retrieval without premature complexity.
- **Positive**: Strict tenant isolation on user memories at the database and service layers.
- **Positive**: Foundation ready for future agent-driven context injection.
