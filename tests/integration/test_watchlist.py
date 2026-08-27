import pytest
from app.services.financial.service import FinancialDataService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def setup_watchlist_service(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    wl_service = WatchlistService(financial_service=fin_service)
    app.extensions["watchlist_service"] = wl_service
    app.extensions["financial_service"] = fin_service
    yield wl_service


def _get_auth_token(client, email: str = "watchlist_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_watchlist_create_authenticated_success(client):
    """Verify adding an item to watchlist as an authenticated user."""
    token = _get_auth_token(client, "wl_creator@example.com")
    res = client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA", "notes": "AI leader", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.get_json()["data"]["item"]
    assert data["symbol"] == "NVDA"
    assert data["notes"] == "AI leader"
    assert data["priority"] == "high"
    assert data["company_name"] == "NVDA Inc."


def test_watchlist_create_unauthenticated_rejected(client):
    """Verify unauthenticated requests return 401."""
    res = client.post("/api/v1/watchlist", json={"symbol": "NVDA"})
    assert res.status_code == 401


def test_watchlist_list_and_filter_by_priority(client):
    """Verify listing watchlist items and filtering by priority."""
    token = _get_auth_token(client, "wl_filter@example.com")

    client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "AAPL", "priority": "low"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List all
    res_all = client.get("/api/v1/watchlist", headers={"Authorization": f"Bearer {token}"})
    assert res_all.status_code == 200
    assert res_all.get_json()["data"]["count"] == 2

    # Filter high
    res_high = client.get("/api/v1/watchlist?priority=high", headers={"Authorization": f"Bearer {token}"})
    assert res_high.status_code == 200
    high_items = res_high.get_json()["data"]["items"]
    assert len(high_items) == 1
    assert high_items[0]["symbol"] == "NVDA"


def test_watchlist_get_update_delete(client):
    """Verify get, update, and delete workflow."""
    token = _get_auth_token(client, "wl_crud@example.com")

    # Create
    res_c = client.post(
        "/api/v1/watchlist",
        json={"symbol": "MSFT", "priority": "normal", "notes": "Init"},
        headers={"Authorization": f"Bearer {token}"},
    )
    item_id = res_c.get_json()["data"]["item"]["id"]

    # Get
    res_g = client.get(f"/api/v1/watchlist/{item_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_g.status_code == 200
    assert res_g.get_json()["data"]["item"]["symbol"] == "MSFT"

    # Update
    res_u = client.put(
        f"/api/v1/watchlist/{item_id}",
        json={"notes": "Updated note", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_u.status_code == 200
    assert res_u.get_json()["data"]["item"]["priority"] == "high"
    assert res_u.get_json()["data"]["item"]["notes"] == "Updated note"

    # Delete
    res_d = client.delete(f"/api/v1/watchlist/{item_id}", headers={"Authorization": f"Bearer {token}"})
    assert res_d.status_code == 200

    # Get after delete returns 404
    assert client.get(f"/api/v1/watchlist/{item_id}", headers={"Authorization": f"Bearer {token}"}).status_code == 404


def test_watchlist_duplicate_symbol_returns_409(client):
    """Verify adding duplicate symbol returns 409 Conflict."""
    token = _get_auth_token(client, "wl_dup@example.com")

    client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    res_dup = client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_dup.status_code == 409
    assert res_dup.get_json()["error"]["code"] == "CONFLICT"


def test_watchlist_validation_errors(client):
    """Verify invalid payloads return 400 Bad Request."""
    token = _get_auth_token(client, "wl_val@example.com")

    # Missing symbol
    assert client.post("/api/v1/watchlist", json={}, headers={"Authorization": f"Bearer {token}"}).status_code == 400

    # Invalid priority
    assert client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA", "priority": "urgent"},
        headers={"Authorization": f"Bearer {token}"},
    ).status_code == 400


def test_watchlist_multi_tenant_isolation(client):
    """
    CRITICAL MULTI-TENANT TEST:
    Verify User A cannot retrieve, update, or delete User B's watchlist items.
    """
    token_a = _get_auth_token(client, "user_a_wl@example.com")
    token_b = _get_auth_token(client, "user_b_wl@example.com")

    # User A creates an item
    res_a = client.post(
        "/api/v1/watchlist",
        json={"symbol": "NVDA", "notes": "User A note"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    item_a_id = res_a.get_json()["data"]["item"]["id"]

    # User B cannot retrieve User A's item (must return 404)
    assert client.get(f"/api/v1/watchlist/{item_a_id}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 404

    # User B cannot update User A's item
    assert client.put(
        f"/api/v1/watchlist/{item_a_id}",
        json={"notes": "Hacked"},
        headers={"Authorization": f"Bearer {token_b}"},
    ).status_code == 404

    # User B cannot delete User A's item
    assert client.delete(f"/api/v1/watchlist/{item_a_id}", headers={"Authorization": f"Bearer {token_b}"}).status_code == 404

    # User A's item remains intact
    res_check = client.get(f"/api/v1/watchlist/{item_a_id}", headers={"Authorization": f"Bearer {token_a}"})
    assert res_check.status_code == 200
    assert res_check.get_json()["data"]["item"]["notes"] == "User A note"


def test_watchlist_client_supplied_user_id_ignored(client):
    """Verify client-supplied user_id payload cannot hijack ownership."""
    token = _get_auth_token(client, "wl_spoof@example.com")

    res = client.post(
        "/api/v1/watchlist",
        json={"symbol": "TSLA", "user_id": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    item_id = res.get_json()["data"]["item"]["id"]

    from app.extensions import db
    from app.models.watchlist import WatchlistItem
    from app.models.user import User

    # Query real user
    user = User.query.filter_by(email="wl_spoof@example.com").first()
    item = db.session.get(WatchlistItem, item_id)
    assert item.user_id == user.id
    assert item.user_id != 9999
