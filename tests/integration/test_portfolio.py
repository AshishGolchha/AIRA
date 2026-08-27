import pytest
from app.extensions import db
from app.models.portfolio import PortfolioHolding
from app.models.user import User
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def setup_portfolio_service(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    app.extensions["portfolio_service"] = pf_service
    app.extensions["financial_service"] = fin_service
    yield pf_service


def _get_auth_token(client, email: str = "portfolio_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_portfolio_create_authenticated_success(client):
    """Verify adding a holding to portfolio as an authenticated user."""
    token = _get_auth_token(client, "pf_creator@example.com")
    res = client.post(
        "/api/v1/portfolio/holdings",
        json={
            "symbol": "NVDA",
            "quantity": 10.5,
            "average_cost": 135.25,
            "notes": "Core position",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.get_json()["data"]["holding"]
    assert data["symbol"] == "NVDA"
    assert data["quantity"] == 10.5
    assert data["average_cost"] == 135.25
    assert data["company_name"] == "NVDA Inc."


def test_portfolio_create_unauthenticated_rejected(client):
    """Verify unauthenticated requests return 401."""
    res = client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
    )
    assert res.status_code == 401


def test_portfolio_list_get_update_delete(client):
    """Verify list, get, update, and delete workflow."""
    token = _get_auth_token(client, "pf_crud@example.com")

    # Create holding
    res_c = client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "MSFT", "quantity": 20, "average_cost": 400.0, "notes": "Initial"},
        headers={"Authorization": f"Bearer {token}"},
    )
    h_id = res_c.get_json()["data"]["holding"]["id"]

    # List
    res_l = client.get("/api/v1/portfolio/holdings", headers={"Authorization": f"Bearer {token}"})
    assert res_l.status_code == 200
    assert res_l.get_json()["data"]["count"] == 1

    # Get
    res_g = client.get(f"/api/v1/portfolio/holdings/{h_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_g.status_code == 200
    assert res_g.get_json()["data"]["holding"]["symbol"] == "MSFT"

    # Update
    res_u = client.put(
        f"/api/v1/portfolio/holdings/{h_id}",
        json={"quantity": 25.5, "average_cost": 405.20, "notes": "Added on dip"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_u.status_code == 200
    updated = res_u.get_json()["data"]["holding"]
    assert updated["quantity"] == 25.5
    assert updated["average_cost"] == 405.20
    assert updated["notes"] == "Added on dip"

    # Delete
    res_d = client.delete(f"/api/v1/portfolio/holdings/{h_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_d.status_code == 200

    # Get after delete returns 404
    assert client.get(f"/api/v1/portfolio/holdings/{h_id}", headers={"Authorization": f"Bearer {token}"}).status_code == 404


def test_portfolio_duplicate_symbol_rejected(client):
    """Verify duplicate symbol per user returns 409 Conflict."""
    token = _get_auth_token(client, "pf_dup@example.com")

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )
    res_dup = client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 5, "average_cost": 120},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_dup.status_code == 409


def test_portfolio_validation_errors(client):
    """Verify invalid inputs return 400 Bad Request."""
    token = _get_auth_token(client, "pf_val@example.com")

    # Missing symbol
    assert client.post(
        "/api/v1/portfolio/holdings",
        json={"quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 400

    # Missing quantity
    assert client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 400

    # Invalid negative quantity
    assert client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": -5, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 400

    # Invalid negative average cost
    assert client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 5, "average_cost": -10},
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 400


def test_portfolio_snapshot_calculations_and_multi_tenant(client):
    """
    CRITICAL PORTFOLIO SNAPSHOT TEST:
    - Verifies deterministic calculations against MockFinancialProvider ($150.0 quote price)
    - Verifies strict user isolation (User A sees only User A's valuation, User B sees only User B's valuation)
    """
    token_a = _get_auth_token(client, "user_a_pf@example.com")
    token_b = _get_auth_token(client, "user_b_pf@example.com")

    # User A has 10 NVDA @ $100 -> Cost Basis = 1000, Market Value = 1500, Gain = 500 (+50.0%)
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B has 20 AAPL @ $150 -> Cost Basis = 3000, Market Value = 3000, Gain = 0 (0.0%)
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "AAPL", "quantity": 20, "average_cost": 150},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # Snapshot for User A
    snap_a = client.get("/api/v1/portfolio/snapshot", headers={"Authorization": f"Bearer {token_a}"}).get_json()["data"]["snapshot"]
    assert snap_a["holdings_count"] == 1
    assert snap_a["total_cost_basis"] == 1000.00
    assert snap_a["total_market_value"] == 1500.00
    assert snap_a["total_unrealized_gain_loss"] == 500.00
    assert snap_a["total_unrealized_gain_loss_percent"] == 50.00
    assert snap_a["holdings"][0]["symbol"] == "NVDA"

    # Snapshot for User B
    snap_b = client.get("/api/v1/portfolio/snapshot", headers={"Authorization": f"Bearer {token_b}"}).get_json()["data"]["snapshot"]
    assert snap_b["holdings_count"] == 1
    assert snap_b["total_cost_basis"] == 3000.00
    assert snap_b["total_market_value"] == 3000.00
    assert snap_b["total_unrealized_gain_loss"] == 0.00
    assert snap_b["total_unrealized_gain_loss_percent"] == 0.00
    assert snap_b["holdings"][0]["symbol"] == "AAPL"


def test_portfolio_multi_tenant_holding_isolation(client):
    """
    CRITICAL MULTI-TENANT TEST:
    Verify User A cannot retrieve, update, or delete User B's portfolio holdings.
    """
    token_a = _get_auth_token(client, "user_a_pf_iso@example.com")
    token_b = _get_auth_token(client, "user_b_pf_iso@example.com")

    # User A creates holding
    res_a = client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    h_a_id = res_a.get_json()["data"]["holding"]["id"]

    # User B cannot retrieve User A's holding
    assert client.get(f"/api/v1/portfolio/holdings/{h_a_id}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 404

    # User B cannot update User A's holding
    assert client.put(
        f"/api/v1/portfolio/holdings/{h_a_id}",
        json={"quantity": 999},
        headers={"Authorization": f"Bearer {token_b}"},
    ).status_code == 404

    # User B cannot delete User A's holding
    assert client.delete(f"/api/v1/portfolio/holdings/{h_a_id}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 404


def test_portfolio_client_supplied_user_id_ignored(client):
    """Verify client-supplied user_id payload cannot hijack holding ownership."""
    token = _get_auth_token(client, "pf_spoof@example.com")

    res = client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "GOOGL", "quantity": 5, "average_cost": 150, "user_id": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    h_id = res.get_json()["data"]["holding"]["id"]

    user = User.query.filter_by(email="pf_spoof@example.com").first()
    holding = db.session.get(PortfolioHolding, h_id)
    assert holding.user_id == user.id
    assert holding.user_id != 9999
