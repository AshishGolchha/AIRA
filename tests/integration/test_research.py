import pytest
from app.services.financial.service import FinancialDataService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def inject_mock_financial_service(app):
    """Injects a mock FinancialDataService into app.extensions for fast, deterministic testing."""
    provider = MockFinancialProvider()
    service = FinancialDataService(provider=provider)
    app.extensions["financial_service"] = service
    yield service


def _get_auth_token(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "researcher@example.com", "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_research_search_authenticated(client):
    """Verify company search / symbol resolution endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/search?q=Nvidia",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["query"] == "Nvidia"
    assert len(data["results"]) == 1
    assert data["results"][0]["symbol"] == "NVDA"


def test_research_search_missing_query(client):
    """Verify 400 when search query is empty."""
    token = _get_auth_token(client)
    res = client.get("/api/v1/research/search", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400
    assert "required" in res.get_json()["error"]["message"]


def test_research_company_profile(client):
    """Verify company profile retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]["profile"]
    assert data["symbol"] == "NVDA"
    assert data["name"] == "NVDA Inc."
    assert data["source"]["provider"] == "mock_provider"
    assert data["source"]["data_type"] == "profile"


def test_research_market_quote(client):
    """Verify market quote retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA/quote",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]["quote"]
    assert data["symbol"] == "NVDA"
    assert data["current_price"] == 150.0
    assert data["source"]["data_type"] == "quote"


def test_research_historical_prices(client):
    """Verify historical prices retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA/history?period=1mo&interval=1d",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]["history"]
    assert data["symbol"] == "NVDA"
    assert data["period"] == "1mo"
    assert len(data["prices"]) == 1


def test_research_financial_statements(client):
    """Verify financial statements retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA/financials?type=income_statement",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]["financials"]
    assert data["symbol"] == "NVDA"
    assert data["statement_type"] == "income_statement"
    assert len(data["periods"]) == 1


def test_research_key_metrics(client):
    """Verify key metrics retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]["metrics"]
    assert data["symbol"] == "NVDA"
    assert data["pe_ratio"] == 25.0
    assert data["source"]["data_type"] == "metrics"


def test_research_company_news(client):
    """Verify company news retrieval endpoint."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/NVDA/news?limit=5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["count"] == 1
    assert data["news"][0]["title"] == "NVDA Reports Record Earnings"
    assert data["news"][0]["source"]["data_type"] == "news"


def test_research_unauthenticated_access(client):
    """Verify unauthenticated requests are rejected with 401."""
    assert client.get("/api/v1/research/company/NVDA").status_code == 401
    assert client.get("/api/v1/research/company/NVDA/quote").status_code == 401
    assert client.get("/api/v1/research/search?q=Nvidia").status_code == 401


def test_research_invalid_symbol_format(client):
    """Verify invalid symbol formats are rejected with 400."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/INVALID$$$",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "Invalid symbol format" in res.get_json()["error"]["message"]


def test_research_company_not_found(client):
    """Verify 404 when company is not found."""
    token = _get_auth_token(client)
    res = client.get(
        "/api/v1/research/company/UNKNOWN",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 404
    assert "not found" in res.get_json()["error"]["message"]
