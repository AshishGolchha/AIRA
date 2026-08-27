import pytest
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.research_service import ResearchService
from tests.unit.test_financial_service import MockFinancialProvider
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


def test_research_service_symbol_resolution_and_validation():
    """Verify ResearchService validates inputs and resolves symbols."""
    provider = MockFinancialProvider()
    fin_service = FinancialDataService(provider=provider)
    service = ResearchService(financial_service=fin_service)

    # Invalid user_id
    with pytest.raises(ValueError, match="Valid authenticated user ID"):
        service.run_research(user_id=0, query="Analyze NVDA")

    # Empty query
    with pytest.raises(ValueError, match="cannot be empty"):
        service.run_research(user_id=1, query="")

    # Resolves ticker directly if query is ticker
    assert service._resolve_target_symbol("AAPL") == "AAPL"

    # Resolves company name via financial service
    assert service._resolve_target_symbol("Nvidia") == "NVDA"


def test_research_service_evidence_grounding_and_user_memory():
    """Verify ground truth facts and sources are assembled and passed into research workflow."""
    mock_supabase = MockSupabaseClient()
    mock_embed = MockEmbeddingService()
    mem_service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embed)
    mem_service.create_memory(
        user_id=1,
        content="I prefer high-growth semiconductor stocks with strong moats.",
        memory_type="preference",
    )

    provider = MockFinancialProvider()
    fin_service = FinancialDataService(provider=provider)

    captured_kwargs = {}

    def mock_crew_runner(symbol, company, query, user_context, facts, sources):
        captured_kwargs["symbol"] = symbol
        captured_kwargs["company"] = company
        captured_kwargs["user_context"] = user_context
        captured_kwargs["facts"] = facts
        captured_kwargs["sources"] = sources
        return {
            "company": company,
            "symbol": symbol,
            "summary": "AI research summary grounded in facts.",
            "facts": facts,
            "fundamentals": "Strong fundamentals based on 25.0 PE ratio.",
            "valuation": "Fairly valued relative to peers.",
            "market_context": "Positive momentum at $150.0 price.",
            "risks": ["Supply chain risk"],
            "opportunities": ["AI data center growth"],
            "user_context": user_context,
            "sources": sources,
        }

    service = ResearchService(
        financial_service=fin_service,
        memory_service=mem_service,
        crew_runner=mock_crew_runner,
    )

    report = service.run_research(user_id=1, query="Analyze NVDA", symbol="NVDA")

    assert report["symbol"] == "NVDA"
    assert report["company"] == "NVDA Inc."
    # Verify factual data directly from provider
    assert report["facts"]["current_price"] == 150.0
    assert report["facts"]["pe_ratio"] == 25.0
    assert report["facts"]["sector"] == "Technology"
    # Verify sources
    assert len(report["sources"]) >= 1
    assert report["sources"][0]["provider"] == "mock_provider"
    # Verify user context
    assert "semiconductor stocks" in report["user_context"]


def test_research_service_rejects_malformed_llm_output_without_fake_fallbacks():
    """Verify that unparseable or broken LLM output raises RuntimeError rather than returning fake fallback claims."""
    provider = MockFinancialProvider()
    fin_service = FinancialDataService(provider=provider)

    # Runner that returns garbage non-JSON string
    def bad_crew_runner(**kwargs):
        return "Sorry, I am an AI and could not format this as JSON."

    service = ResearchService(
        financial_service=fin_service,
        crew_runner=bad_crew_runner,
    )

    with pytest.raises(RuntimeError, match="Failed to produce valid structured research report"):
        service.run_research(user_id=1, query="Analyze NVDA", symbol="NVDA")
