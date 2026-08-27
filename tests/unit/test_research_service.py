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


def test_research_service_user_memory_context_injection():
    """Verify user memory is retrieved and injected into the research context."""
    # 1. Setup mock memory store with user memory
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

    captured_context = {}

    def mock_crew_runner(symbol, company, query, user_context):
        captured_context["symbol"] = symbol
        captured_context["company"] = company
        captured_context["user_context"] = user_context
        return {
            "company": company,
            "symbol": symbol,
            "summary": "AI research summary",
            "fundamentals": "Strong fundamentals",
            "valuation": "Fairly valued",
            "market_context": "Bullish momentum",
            "risks": ["Supply chain risk"],
            "opportunities": ["AI data center growth"],
            "user_context": user_context,
            "sources": [{"provider": "yfinance", "symbol": symbol}],
        }

    service = ResearchService(
        financial_service=fin_service,
        memory_service=mem_service,
        crew_runner=mock_crew_runner,
    )

    report = service.run_research(user_id=1, query="Analyze NVDA", symbol="NVDA")

    assert report["symbol"] == "NVDA"
    assert report["company"] == "NVDA Inc."
    assert "semiconductor stocks" in captured_context["user_context"]
    assert report["user_context"] == captured_context["user_context"]
