import pytest
from app.services.financial.service import FinancialDataService
from app.services.memory_service import MemoryService
from app.services.research_service import ResearchService
from tests.unit.test_financial_service import MockFinancialProvider
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


@pytest.fixture(autouse=True)
def setup_research_service(app):
    """Injects a mock ResearchService into app.extensions for fast, offline testing."""
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
            "fundamentals": "Strong revenue growth and robust operational margins.",
            "valuation": "Trading at a fair multiple relative to peer averages.",
            "market_context": "Positive institutional sentiment and steady volume.",
            "risks": ["Regulatory scrutiny", "Market volatility"],
            "opportunities": ["Global expansion", "New product launches"],
            "user_context": user_context,
            "sources": sources or [
                {
                    "provider": "yfinance",
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


def _get_auth_token(client, email: str = "ai_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_ai_research_analyze_authenticated_success(client):
    """Verify authenticated user can trigger AI research workflow on a company."""
    token = _get_auth_token(client, email="analyst_user@example.com")

    payload = {
        "symbol": "NVDA",
        "query": "Analyze NVIDIA as a long-term investment opportunity",
    }
    res = client.post(
        "/api/v1/research/analyze",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    report = data["data"]["report"]
    assert report["symbol"] == "NVDA"
    assert report["company"] == "NVDA Inc."
    # Verified facts separation
    assert "facts" in report
    assert report["facts"]["current_price"] == 150.0
    assert report["facts"]["pe_ratio"] == 25.0
    assert "summary" in report
    assert "fundamentals" in report
    assert "valuation" in report
    assert "risks" in report
    assert "opportunities" in report
    assert len(report["sources"]) >= 1
    assert report["sources"][0]["provider"] == "mock_provider"


def test_ai_research_analyze_unauthenticated(client):
    """Verify unauthenticated request is rejected with 401."""
    res = client.post("/api/v1/research/analyze", json={"symbol": "NVDA", "query": "Analyze"})
    assert res.status_code == 401


def test_ai_research_analyze_missing_inputs(client):
    """Verify 400 when neither query nor symbol is supplied."""
    token = _get_auth_token(client, email="empty_user@example.com")
    res = client.post(
        "/api/v1/research/analyze",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]["message"]


def test_ai_research_user_memory_isolation_and_personalization(client):
    """
    CRITICAL SECURITY & INTEGRATION TEST:
    Verify that User A's research includes ONLY User A's personal memory context,
    and User B's research includes ONLY User B's personal memory context.
    """
    # 1. Register User A and User B
    token_a = _get_auth_token(client, email="user_a_ai@example.com")
    token_b = _get_auth_token(client, email="user_b_ai@example.com")

    # 2. Store personalized memory for User A
    client.post(
        "/api/v1/memory",
        json={"content": "User A prefers aggressive tech growth and AI hardware"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # 3. Store personalized memory for User B
    client.post(
        "/api/v1/memory",
        json={"content": "User B prefers conservative dividend-paying utility stocks"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # 4. User A requests research (with an attempted client-supplied user_id tamper)
    res_a = client.post(
        "/api/v1/research/analyze",
        json={
            "user_id": 999,  # Malicious client-supplied ID (must be ignored)
            "symbol": "NVDA",
            "query": "Is NVIDIA a fit for my portfolio?",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert res_a.status_code == 200
    report_a = res_a.get_json()["data"]["report"]
    assert "User A prefers aggressive tech growth" in report_a["user_context"]
    assert "User B" not in report_a["user_context"]

    # 5. User B requests research
    res_b = client.post(
        "/api/v1/research/analyze",
        json={
            "symbol": "NVDA",
            "query": "Is NVIDIA a fit for my portfolio?",
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert res_b.status_code == 200
    report_b = res_b.get_json()["data"]["report"]
    assert "User B prefers conservative dividend-paying" in report_b["user_context"]
    assert "User A" not in report_b["user_context"]


def test_ai_research_malformed_llm_output_fails_safely(app, client):
    """Verify that if LLM returns malformed or non-JSON output, API returns safe 500 error instead of fake report."""
    def broken_runner(**kwargs):
        return "Non-JSON unparseable output."

    app.extensions["research_service"] = ResearchService(
        financial_service=FinancialDataService(provider=MockFinancialProvider()),
        memory_service=app.extensions.get("memory_service"),
        crew_runner=broken_runner,
    )

    token = _get_auth_token(client, email="malformed_test@example.com")
    res = client.post(
        "/api/v1/research/analyze",
        json={"symbol": "NVDA", "query": "Analyze NVIDIA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 500
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
