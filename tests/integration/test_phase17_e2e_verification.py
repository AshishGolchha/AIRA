"""
End-to-End Programmatic Integration Test for AIRA Phase 17.
Verifies complete client-server flow matching the frontend API client.
"""
import pytest


def test_phase17_full_client_server_integration(client):
    # 1. Register User (matches frontend Auth.register)
    reg_payload = {
        "email": "e2e_investor@aira.internal",
        "password": "ProductionPassword123!",
        "display_name": "E2E Master Investor",
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    token = data["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile & Update Preferences (matches Settings.tsx)
    p_res = client.get("/api/v1/profile", headers=headers)
    assert p_res.status_code == 200
    p_data = p_res.get_json()["data"]["profile"]
    assert p_data["display_name"] == "E2E Master Investor"

    p_update = client.put(
        "/api/v1/profile",
        headers=headers,
        json={
            "investment_focus": "Semiconductor & AI Infrastructure",
            "risk_preference": "aggressive",
            "investment_horizon": "long_term",
        },
    )
    assert p_update.status_code == 200

    # 3. Create Portfolio Holding (matches Portfolio.tsx)
    h_res = client.post(
        "/api/v1/portfolio/holdings",
        headers=headers,
        json={
            "symbol": "NVDA",
            "quantity": 50,
            "average_cost": 120.0,
            "notes": "Core position",
        },
    )
    assert h_res.status_code == 201
    holding_id = h_res.get_json()["data"]["holding"]["id"]

    # 4. Get Portfolio Snapshot (matches Portfolio.tsx snapshot card)
    snap_res = client.get("/api/v1/portfolio/snapshot", headers=headers)
    assert snap_res.status_code == 200
    snap_data = snap_res.get_json()["data"]["snapshot"]
    assert snap_data["holdings_count"] == 1
    assert snap_data["total_cost_basis"] == 6000.0

    # 5. Add to Watchlist (matches Watchlist.tsx)
    w_res = client.post(
        "/api/v1/watchlist",
        headers=headers,
        json={
            "symbol": "AMD",
            "priority": "high",
            "notes": "MI300 ramp catalyst",
        },
    )
    assert w_res.status_code == 201

    # 6. Run Alert Evaluation (matches Alerts.tsx)
    a_res = client.post("/api/v1/alerts/check", headers=headers)
    assert a_res.status_code == 200
    assert "created_count" in a_res.get_json()["data"]
    assert "alerts" in a_res.get_json()["data"]

    # 7. Update Notification Preferences & Add Webhook (matches Notifications.tsx)
    n_pref = client.put(
        "/api/v1/notifications/preferences",
        headers=headers,
        json={
            "in_app_enabled": True,
            "email_enabled": True,
            "webhook_enabled": True,
            "minimum_severity": "warning",
            "alert_types": ["price_move", "portfolio_gain_loss"],
        },
    )
    assert n_pref.status_code == 200

    ep_res = client.post(
        "/api/v1/notifications/endpoints",
        headers=headers,
        json={
            "endpoint_url": "https://webhook.site/test-aira-123",
            "secret_key": "webhook_hmac_secret_key_123",
        },
    )
    assert ep_res.status_code == 201
    ep_data = ep_res.get_json()["data"]["endpoint"]
    assert "secret_key" not in ep_data  # Secret key is safely hidden

    # 8. Unified Read-Only Dashboard Snapshot (matches Dashboard.tsx)
    dash_res = client.get("/api/v1/dashboard", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.get_json()["data"]
    assert dash_data["user"]["name"] == "E2E Master Investor"
    assert dash_data["portfolio"]["holdings_count"] == 1
    assert dash_data["watchlist"]["total_count"] == 1
    assert "alerts" in dash_data
    assert "notifications" in dash_data
    assert "monitoring" in dash_data
    assert "portfolio_intelligence" in dash_data
