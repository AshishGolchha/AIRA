import pytest
from app.extensions import db
from app.models.portfolio import PortfolioHolding
from app.models.portfolio_intelligence import PortfolioIntelligenceRecord
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
            "portfolio_overview": f"Portfolio contains {len(portfolio_context)} assets.",
            "portfolio_risks": [f"Sector exposure concentrated in {holdings_symbols[0]}"] if holdings_symbols else [],
            "portfolio_opportunities": ["Expanding AI profitability trends"],
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


def _get_auth_token(client, email: str = "intel_hist_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_portfolio_intelligence_persists_record_and_returns_id(client):
    """Verify that generating portfolio intelligence automatically persists a record with an ID."""
    token = _get_auth_token(client, "persist_intel_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers)
    client.post("/api/v1/watchlist", json={"symbol": "AAPL", "priority": "high"}, headers=headers)

    res = client.post("/api/v1/portfolio/intelligence", json={"query": "Evaluate risks"}, headers=headers)
    assert res.status_code == 200
    data = res.get_json()["data"]["intelligence"]
    assert "id" in data
    assert data["id"] is not None
    assert "created_at" in data

    # Verify directly in database
    record = db.session.get(PortfolioIntelligenceRecord, data["id"])
    assert record is not None
    assert "NVDA" in record.summary
    assert "facts" in record.to_dict()
    assert record.facts["portfolio_totals"]["total_market_value"] == 1500.0


def test_list_portfolio_intelligence_history_and_pagination(client):
    """Verify listing intelligence history returns lightweight summaries with bounded pagination."""
    token = _get_auth_token(client, "list_intel_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers)

    # Generate 3 reports
    for i in range(3):
        client.post("/api/v1/portfolio/intelligence", json={"query": f"Query {i}"}, headers=headers)

    # Query history with page=1&limit=2
    res = client.get("/api/v1/portfolio/intelligence/history?page=1&limit=2", headers=headers)
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert data["total"] == 3
    assert data["count"] == 2
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["history"]) == 2
    # Verify lightweight representation
    assert "summary" in data["history"][0]
    assert "symbols_analyzed" in data["history"][0]
    assert "facts" not in data["history"][0]


def test_get_and_delete_single_intelligence_report(client):
    """Verify retrieving full report by ID and deleting it."""
    token = _get_auth_token(client, "single_intel_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers)
    res_gen = client.post("/api/v1/portfolio/intelligence", json={"query": "Single report test"}, headers=headers)
    intel_id = res_gen.get_json()["data"]["intelligence"]["id"]

    # 1. Retrieve full report
    res_get = client.get(f"/api/v1/portfolio/intelligence/history/{intel_id}", headers=headers)
    assert res_get.status_code == 200
    report = res_get.get_json()["data"]["report"]
    assert report["id"] == intel_id
    assert "facts" in report
    assert "sources" in report
    assert "portfolio_overview" in report

    # 2. Delete report
    res_del = client.delete(f"/api/v1/portfolio/intelligence/history/{intel_id}", headers=headers)
    assert res_del.status_code == 200

    # 3. Retrieve after delete returns 404
    assert client.get(f"/api/v1/portfolio/intelligence/history/{intel_id}", headers=headers).status_code == 404


def test_intelligence_history_unauthenticated_rejected(client):
    """Verify unauthenticated requests return 401."""
    assert client.get("/api/v1/portfolio/intelligence/history").status_code == 401
    assert client.get("/api/v1/portfolio/intelligence/history/1").status_code == 401
    assert client.delete("/api/v1/portfolio/intelligence/history/1").status_code == 401


def test_intelligence_history_multi_tenant_isolation(client):
    """
    CRITICAL MULTI-TENANT TEST:
    Verify User A cannot list, view by ID, or delete User B's intelligence reports.
    """
    token_a = _get_auth_token(client, "user_a_intel_iso@example.com")
    token_b = _get_auth_token(client, "user_b_intel_iso@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A has NVDA
    client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers_a)
    res_a = client.post("/api/v1/portfolio/intelligence", headers=headers_a)
    id_a = res_a.get_json()["data"]["intelligence"]["id"]

    # User B has TSLA
    client.post("/api/v1/portfolio/holdings", json={"symbol": "TSLA", "quantity": 20, "average_cost": 200}, headers=headers_b)
    res_b = client.post("/api/v1/portfolio/intelligence", headers=headers_b)
    id_b = res_b.get_json()["data"]["intelligence"]["id"]

    # Check User A history: contains only A
    hist_a = client.get("/api/v1/portfolio/intelligence/history", headers=headers_a).get_json()["data"]
    assert hist_a["total"] == 1
    assert hist_a["history"][0]["id"] == id_a

    # Check User B history: contains only B
    hist_b = client.get("/api/v1/portfolio/intelligence/history", headers=headers_b).get_json()["data"]
    assert hist_b["total"] == 1
    assert hist_b["history"][0]["id"] == id_b

    # User A cannot retrieve User B's report (returns 404, not 403, preventing enumeration)
    assert client.get(f"/api/v1/portfolio/intelligence/history/{id_b}", headers=headers_a).status_code == 404

    # User B cannot retrieve User A's report
    assert client.get(f"/api/v1/portfolio/intelligence/history/{id_a}", headers=headers_b).status_code == 404

    # User A cannot delete User B's report
    assert client.delete(f"/api/v1/portfolio/intelligence/history/{id_b}", headers=headers_a).status_code == 404

    # User B's report remains intact
    assert client.get(f"/api/v1/portfolio/intelligence/history/{id_b}", headers=headers_b).status_code == 200


def test_snapshot_semantics_immutable_after_portfolio_modifications(client):
    """
    CRITICAL SNAPSHOT SEMANTICS TEST:
    Modifying portfolio holdings later must NOT alter historical intelligence records.
    """
    token = _get_auth_token(client, "snapshot_test_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create holding: 10 NVDA @ $100 -> Market Value = $1500
    res_hold = client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers)
    holding_id = res_hold.get_json()["data"]["holding"]["id"]

    # 2. Generate intelligence report
    res_gen = client.post("/api/v1/portfolio/intelligence", headers=headers)
    intel_id = res_gen.get_json()["data"]["intelligence"]["id"]

    # 3. User modifies NVDA quantity to 100 shares
    client.put(f"/api/v1/portfolio/holdings/{holding_id}", json={"quantity": 100, "average_cost": 100}, headers=headers)

    # 4. Fetch the historical report
    res_get = client.get(f"/api/v1/portfolio/intelligence/history/{intel_id}", headers=headers)
    assert res_get.status_code == 200
    historical_facts = res_get.get_json()["data"]["report"]["facts"]

    # 5. Historical report must still reflect 10 shares ($1500 market value)
    assert historical_facts["holdings"]["NVDA"]["quantity"] == 10.0
    assert historical_facts["portfolio_totals"]["total_market_value"] == 1500.0


def test_malformed_ai_output_persists_zero_records(app, client):
    """Verify that failing or malformed AI synthesis creates zero database records."""
    def broken_runner(**kwargs):
        raise RuntimeError("LLM synthesis failed")

    app.extensions["portfolio_intelligence_service"] = PortfolioIntelligenceService(
        portfolio_service=app.extensions["portfolio_service"],
        watchlist_service=app.extensions["watchlist_service"],
        financial_service=app.extensions["financial_service"],
        memory_service=app.extensions["memory_service"],
        crew_runner=broken_runner,
    )

    token = _get_auth_token(client, "fail_safety_intel@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/v1/portfolio/holdings", json={"symbol": "NVDA", "quantity": 10, "average_cost": 100}, headers=headers)

    # Request intelligence (should fail with 500)
    res = client.post("/api/v1/portfolio/intelligence", headers=headers)
    assert res.status_code == 500

    # Ensure 0 records were persisted in history
    hist = client.get("/api/v1/portfolio/intelligence/history", headers=headers).get_json()["data"]
    assert hist["total"] == 0
