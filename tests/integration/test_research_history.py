import pytest
from app.models.research import ResearchRecord
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.research_service import ResearchService
from tests.unit.test_financial_service import MockFinancialProvider
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


@pytest.fixture(autouse=True)
def setup_research_service(app):
    """Injects a mock ResearchService into app.extensions for deterministic testing."""
    mock_supabase = MockSupabaseClient()
    mock_embedding = MockEmbeddingService()
    mem_service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embedding)
    fin_service = FinancialDataService(provider=MockFinancialProvider())

    def mock_crew_runner(symbol, company, query, user_context, facts=None, sources=None):
        return {
            "company": company,
            "symbol": symbol,
            "summary": f"Comprehensive AI investment report for {company} ({symbol}).",
            "facts": facts or {
                "name": company,
                "current_price": 150.0,
                "pe_ratio": 25.0,
                "sector": "Technology",
            },
            "fundamentals": "Strong revenue growth.",
            "valuation": "Fair multiple.",
            "market_context": "Positive momentum.",
            "risks": ["Supply chain", "Regulatory"],
            "opportunities": ["AI market growth"],
            "user_context": user_context,
            "sources": sources or [
                {
                    "provider": "mock_provider",
                    "source_url": f"https://finance.yahoo.com/quote/{symbol}",
                    "data_type": "profile",
                    "symbol": symbol,
                }
            ],
        }

    research_service = ResearchService(
        financial_service=fin_service,
        memory_service=mem_service,
        crew_runner=mock_crew_runner,
    )

    app.extensions["research_service"] = research_service
    app.extensions["memory_service"] = mem_service
    app.extensions["financial_service"] = fin_service
    yield research_service


def _get_auth_token(client, email: str = "history_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_research_analysis_persists_record_and_returns_id(client):
    """Verify that running research analysis automatically persists a ResearchRecord."""
    token = _get_auth_token(client, email="persist_user@example.com")

    res = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVIDIA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    report = res.get_json()["data"]["report"]
    assert "id" in report
    assert report["id"] is not None

    # Check database record
    from app.extensions import db

    record = db.session.get(ResearchRecord, report["id"])
    assert record is not None
    assert record.symbol == "NVDA"
    assert record.company == "NVDA Inc."
    assert record.facts["current_price"] == 150.0
    assert len(record.sources) >= 1


def test_list_research_history_and_pagination(client):
    """Verify listing research history returns lightweight summaries with pagination."""
    token = _get_auth_token(client, email="history_list_user@example.com")

    # Create 3 research analyses
    client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVDA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/research/analyze",
        json={"symbol": "AAPL", "query": "Analyze AAPL"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/research/analyze",
        json={"symbol": "MSFT", "query": "Analyze MSFT"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get history
    res = client.get(
        "/api/v1/research/history?page=1&limit=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total"] == 3
    assert data["count"] == 2
    assert len(data["history"]) == 2
    # Verify lightweight representation
    assert "summary" in data["history"][0]
    assert "facts" not in data["history"][0]


def test_get_and_delete_single_research_report(client):
    """Verify retrieving and deleting a single research report."""
    token = _get_auth_token(client, email="single_report_user@example.com")

    # 1. Create report
    res_create = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVIDIA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    report_id = res_create.get_json()["data"]["report"]["id"]

    # 2. Retrieve full report by ID
    res_get = client.get(
        f"/api/v1/research/history/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_get.status_code == 200
    report = res_get.get_json()["data"]["report"]
    assert report["id"] == report_id
    assert report["symbol"] == "NVDA"
    assert "facts" in report
    assert "sources" in report

    # 3. Delete report
    res_del = client.delete(
        f"/api/v1/research/history/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_del.status_code == 200

    # 4. Verify 404 after deletion
    res_get_after = client.get(
        f"/api/v1/research/history/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_get_after.status_code == 404


def test_research_history_unauthenticated_rejected(client):
    """Verify unauthenticated history endpoints return 401."""
    assert client.get("/api/v1/research/history").status_code == 401
    assert client.get("/api/v1/research/history/1").status_code == 401
    assert client.delete("/api/v1/research/history/1").status_code == 401


def test_research_history_multi_user_isolation(client):
    """
    CRITICAL MULTI-TENANT ISOLATION TEST:
    Verify that User A cannot view, retrieve by ID, or delete User B's research records.
    """
    token_a = _get_auth_token(client, email="user_a_history@example.com")
    token_b = _get_auth_token(client, email="user_b_history@example.com")

    # User A creates a report
    res_a = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVDA for User A"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    report_id_a = res_a.get_json()["data"]["report"]["id"]

    # User B creates a report
    res_b = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "AAPL", "query": "Analyze AAPL for User B"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    report_id_b = res_b.get_json()["data"]["report"]["id"]

    # User A history contains only Report A
    hist_a = client.get("/api/v1/research/history", headers={"Authorization": f"Bearer {token_a}"}).get_json()["data"]
    assert hist_a["total"] == 1
    assert hist_a["history"][0]["id"] == report_id_a

    # User B history contains only Report B
    hist_b = client.get("/api/v1/research/history", headers={"Authorization": f"Bearer {token_b}"}).get_json()["data"]
    assert hist_b["total"] == 1
    assert hist_b["history"][0]["id"] == report_id_b

    # User A cannot retrieve User B's report (must return 404, not 403, preventing enumeration)
    assert client.get(f"/api/v1/research/history/{report_id_b}", headers={"Authorization": f"Bearer {token_a}"}).status_code == 404

    # User B cannot retrieve User A's report
    assert client.get(f"/api/v1/research/history/{report_id_a}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 404

    # User A cannot delete User B's report
    assert client.delete(f"/api/v1/research/history/{report_id_b}", headers={"Authorization": f"Bearer {token_a}"}).status_code == 404

    # User B's report is still intact
    assert client.get(f"/api/v1/research/history/{report_id_b}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 200


def test_failure_safety_persists_zero_records_on_error(app, client):
    """Verify that failed or malformed research workflows persist zero incomplete records."""
    def broken_runner(**kwargs):
        raise RuntimeError("LLM failure during synthesis.")

    app.extensions["research_service"] = ResearchService(
        financial_service=FinancialDataService(provider=MockFinancialProvider()),
        memory_service=app.extensions.get("memory_service"),
        crew_runner=broken_runner,
    )

    token = _get_auth_token(client, email="failure_test_user@example.com")
    res = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVDA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 500

    # Ensure no record was created
    hist = client.get("/api/v1/research/history", headers={"Authorization": f"Bearer {token}"}).get_json()["data"]
    assert hist["total"] == 0
