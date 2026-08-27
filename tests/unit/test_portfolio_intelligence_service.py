import pytest
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.portfolio_intelligence_service import PortfolioIntelligenceService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


@pytest.fixture
def services(app):
    mock_supabase = MockSupabaseClient()
    mock_embed = MockEmbeddingService()
    mem_service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embed)
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    res_service = ResearchService(financial_service=fin_service, memory_service=mem_service)

    return {
        "memory_service": mem_service,
        "financial_service": fin_service,
        "portfolio_service": pf_service,
        "watchlist_service": wl_service,
        "research_service": res_service,
    }


def test_portfolio_intelligence_validation(services):
    """Verify input validation for user_id."""
    intel_service = PortfolioIntelligenceService(
        portfolio_service=services["portfolio_service"],
        watchlist_service=services["watchlist_service"],
        financial_service=services["financial_service"],
        memory_service=services["memory_service"],
        research_service=services["research_service"],
    )

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        intel_service.run_portfolio_intelligence(user_id=0)

    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        intel_service.run_portfolio_intelligence(user_id=-1)


def test_portfolio_intelligence_empty_portfolio_and_watchlist(app, services):
    """Verify empty investment universe returns graceful structured report without hallucination."""
    intel_service = PortfolioIntelligenceService(
        portfolio_service=services["portfolio_service"],
        watchlist_service=services["watchlist_service"],
        financial_service=services["financial_service"],
        memory_service=services["memory_service"],
        research_service=services["research_service"],
    )

    report = intel_service.run_portfolio_intelligence(user_id=1)
    assert "No investment holdings" in report["summary"]
    assert report["portfolio_risks"] == []
    assert report["portfolio_opportunities"] == []
    assert len(report["recommended_research"]) >= 1
    assert report["portfolio_summary"]["holdings_count"] == 0


def test_portfolio_intelligence_deterministic_context_and_weights(app, services):
    """Verify deterministic calculation of portfolio weights and context assembly."""
    # Setup holding: 10 NVDA @ $100 (Market price $150 in mock -> MV = 1500)
    services["portfolio_service"].create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)
    # Setup holding: 5 MSFT @ $100 (Market price $150 in mock -> MV = 750)
    services["portfolio_service"].create_holding(user_id=1, symbol="MSFT", quantity=5, average_cost=100)
    # Setup watchlist item
    services["watchlist_service"].add_item(user_id=1, symbol="AAPL", priority="high", notes="Watch for breakout")

    captured_kwargs = {}

    def mock_crew_runner(query, portfolio_context, watchlist_context, user_context, facts, sources):
        captured_kwargs["portfolio_context"] = portfolio_context
        captured_kwargs["watchlist_context"] = watchlist_context
        captured_kwargs["facts"] = facts
        return {
            "summary": "Diversified portfolio with semiconductor and enterprise cloud exposure.",
            "portfolio_overview": "Healthy asset allocation with total market value $2250.",
            "portfolio_risks": ["NVDA represents 66.67% of equity allocation"],
            "portfolio_opportunities": ["Expanding margins in MSFT position"],
            "watchlist_priorities": ["AAPL: High priority monitor for entry"],
            "recommended_research": ["Deep dive into AAPL services revenue"],
        }

    intel_service = PortfolioIntelligenceService(
        portfolio_service=services["portfolio_service"],
        watchlist_service=services["watchlist_service"],
        financial_service=services["financial_service"],
        memory_service=services["memory_service"],
        research_service=services["research_service"],
        crew_runner=mock_crew_runner,
    )

    report = intel_service.run_portfolio_intelligence(user_id=1, query="Assess portfolio risk")

    # Verify report structure
    assert report["summary"] == "Diversified portfolio with semiconductor and enterprise cloud exposure."
    assert len(report["portfolio_risks"]) == 1
    assert report["portfolio_summary"]["total_market_value"] == 2250.00
    assert report["portfolio_summary"]["total_cost_basis"] == 1500.00
    assert report["portfolio_summary"]["total_unrealized_gain_loss"] == 750.00
    assert report["portfolio_summary"]["total_unrealized_gain_loss_percent"] == 50.00

    # Verify deterministic weights passed to AI context
    pf_ctx = captured_kwargs["portfolio_context"]
    nvda_h = next(h for h in pf_ctx if h["symbol"] == "NVDA")
    assert nvda_h["weight_percent"] == 66.67  # (1500 / 2250) * 100
    msft_h = next(h for h in pf_ctx if h["symbol"] == "MSFT")
    assert msft_h["weight_percent"] == 33.33  # (750 / 2250) * 100

    # Verify watchlist context
    wl_ctx = captured_kwargs["watchlist_context"]
    assert len(wl_ctx) == 1
    assert wl_ctx[0]["symbol"] == "AAPL"
    assert wl_ctx[0]["priority"] == "high"


def test_portfolio_intelligence_malformed_llm_output_fails_safely(app, services):
    """Verify malformed LLM output safely raises RuntimeError."""
    services["portfolio_service"].create_holding(user_id=1, symbol="NVDA", quantity=10, average_cost=100)

    def broken_runner(**kwargs):
        return "Not valid json response."

    intel_service = PortfolioIntelligenceService(
        portfolio_service=services["portfolio_service"],
        watchlist_service=services["watchlist_service"],
        financial_service=services["financial_service"],
        memory_service=services["memory_service"],
        research_service=services["research_service"],
        crew_runner=broken_runner,
    )

    with pytest.raises(RuntimeError, match="Failed to produce valid structured portfolio intelligence"):
        intel_service.run_portfolio_intelligence(user_id=1)
