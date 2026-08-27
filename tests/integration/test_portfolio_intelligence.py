import pytest
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.portfolio_intelligence_service import PortfolioIntelligenceService
from app.services.portfolio_service import PortfolioService
from app.services.research_service import ResearchService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


@pytest.fixture(autouse=True)
def setup_portfolio_intelligence(app):
    mock_supabase = MockSupabaseClient()
    mock_embed = MockEmbeddingService()
    mem_service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embed)
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    res_service = ResearchService(financial_service=fin_service, memory_service=mem_service)

    def mock_crew_runner(query, portfolio_context, watchlist_context, user_context, facts, sources):
        holdings_symbols = [h["symbol"] for h in portfolio_context]
        watchlist_symbols = [w["symbol"] for w in watchlist_context]
        return {
            "summary": f"Personalized portfolio intelligence analyzing holdings: {', '.join(holdings_symbols)}.",
            "portfolio_overview": f"Portfolio contains {len(portfolio_context)} assets with verified valuation context.",
            "portfolio_risks": [f"Sector exposure concentrated in {holdings_symbols[0]}"] if holdings_symbols else [],
            "portfolio_opportunities": ["Expanding profitability trends"],
            "watchlist_priorities": [f"Monitor {sym} for entry point" for sym in watchlist_symbols],
            "recommended_research": [f"Conduct deep analysis on {sym}" for sym in watchlist_symbols or ["broad market"]],
        }

    intel_service = PortfolioIntelligenceService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
        memory_service=mem_service,
        research_service=res_service,
        crew_runner=mock_crew_runner,
    )

    app.extensions["portfolio_intelligence_service"] = intel_service
    app.extensions["portfolio_service"] = pf_service
    app.extensions["watchlist_service"] = wl_service
    app.extensions["memory_service"] = mem_service
    app.extensions["financial_service"] = fin_service
    app.extensions["research_service"] = res_service

    yield intel_service


def _get_auth_token(client, email: str = "intel_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_portfolio_intelligence_authenticated_success(client):
    """Verify authenticated user receives personalized intelligence for their portfolio and watchlist."""
    token = _get_auth_token(client, "intel_auth_success@example.com")

    # 1. Add portfolio holding
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 2. Add watchlist item
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "AAPL", "priority": "high", "notes": "Ecosystem leader"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. Add personal memory
    client.post(
        "/api/v1/memory",
        json={"content": "I prefer high-growth AI semiconductor positions with long-term horizon", "memory_type": "preference"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 4. Request intelligence
    res = client.post(
        "/api/v1/portfolio/intelligence",
        json={"query": "Evaluate my current allocation and risks"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    intel = res.get_json()["data"]["intelligence"]

    assert "NVDA" in intel["summary"]
    assert "NVDA" in intel["portfolio_risks"][0]
    assert "AAPL" in intel["watchlist_priorities"][0]
    assert intel["portfolio_summary"]["holdings_count"] == 1
    assert intel["portfolio_summary"]["total_market_value"] == 1500.00
    assert "high-growth AI semiconductor" in intel["user_context"]
    assert len(intel["sources"]) >= 1


def test_portfolio_intelligence_unauthenticated_rejected(client):
    """Verify unauthenticated request returns 401."""
    res = client.post("/api/v1/portfolio/intelligence", json={})
    assert res.status_code == 401


def test_portfolio_intelligence_empty_state_graceful(client):
    """Verify user with empty portfolio and watchlist receives graceful non-crashing response."""
    token = _get_auth_token(client, "intel_empty@example.com")

    res = client.post(
        "/api/v1/portfolio/intelligence",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    intel = res.get_json()["data"]["intelligence"]
    assert "No investment holdings" in intel["summary"]
    assert intel["portfolio_summary"]["holdings_count"] == 0
    assert intel["portfolio_risks"] == []


def test_portfolio_intelligence_multi_tenant_isolation(client):
    """
    CRITICAL MULTI-TENANT ISOLATION TEST:
    Verify User A cannot see User B's portfolio holdings, watchlist items, or memories.
    """
    token_a = _get_auth_token(client, "user_a_intel@example.com")
    token_b = _get_auth_token(client, "user_b_intel@example.com")

    # User A has NVDA holding & TSLA on watchlist & User A memory
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "TSLA", "priority": "high"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    client.post(
        "/api/v1/memory",
        json={"content": "Secret User A Strategy: buy semiconductors", "memory_type": "preference"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B has MSFT holding & GOOGL on watchlist & User B memory
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "MSFT", "quantity": 20, "average_cost": 200},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "GOOGL", "priority": "normal"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    client.post(
        "/api/v1/memory",
        json={"content": "Secret User B Strategy: enterprise cloud only", "memory_type": "preference"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # User A runs intelligence: must see NVDA and TSLA, NEVER MSFT, GOOGL, or User B's strategy
    res_a = client.post("/api/v1/portfolio/intelligence", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    intel_a = res_a.get_json()["data"]["intelligence"]
    assert "NVDA" in intel_a["summary"]
    assert "TSLA" in intel_a["watchlist_priorities"][0]
    assert "User A Strategy" in intel_a["user_context"]
    assert "MSFT" not in intel_a["summary"]
    assert "GOOGL" not in str(intel_a["watchlist_priorities"])
    assert "User B Strategy" not in intel_a["user_context"]

    # User B runs intelligence: must see MSFT and GOOGL, NEVER NVDA, TSLA, or User A's strategy
    res_b = client.post("/api/v1/portfolio/intelligence", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    intel_b = res_b.get_json()["data"]["intelligence"]
    assert "MSFT" in intel_b["summary"]
    assert "GOOGL" in intel_b["watchlist_priorities"][0]
    assert "User B Strategy" in intel_b["user_context"]
    assert "NVDA" not in intel_b["summary"]
    assert "TSLA" not in str(intel_b["watchlist_priorities"])
    assert "User A Strategy" not in intel_b["user_context"]


def test_portfolio_intelligence_malformed_ai_fails_safely(app, client):
    """Verify malformed LLM response safely returns standard 500 error envelope."""
    def broken_runner(**kwargs):
        raise RuntimeError("LLM service unavailable")

    app.extensions["portfolio_intelligence_service"] = PortfolioIntelligenceService(
        portfolio_service=app.extensions["portfolio_service"],
        watchlist_service=app.extensions["watchlist_service"],
        financial_service=app.extensions["financial_service"],
        memory_service=app.extensions["memory_service"],
        crew_runner=broken_runner,
    )

    token = _get_auth_token(client, "intel_fail@example.com")
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.post(
        "/api/v1/portfolio/intelligence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 500
    assert res.get_json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
