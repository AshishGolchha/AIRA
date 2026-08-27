def _get_auth_token(client, email: str = "pref_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_get_preferences_default(client):
    """Verify authenticated user receives default notification preferences."""
    token = _get_auth_token(client, "user_default_pref@example.com")
    resp = client.get(
        "/api/v1/notifications/preferences",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]["preferences"]
    assert data["in_app_enabled"] is True
    assert data["email_enabled"] is True
    assert data["webhook_enabled"] is False
    assert data["minimum_severity"] == "info"
    assert data["alert_types"] is None


def test_update_preferences_success(client):
    """Verify updating preferences with custom channels, severity, and alert types."""
    token = _get_auth_token(client, "user_update_pref@example.com")
    resp = client.put(
        "/api/v1/notifications/preferences",
        json={
            "in_app_enabled": True,
            "email_enabled": False,
            "webhook_enabled": True,
            "minimum_severity": "warning",
            "alert_types": ["portfolio_loss", "price_move"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()["data"]["preferences"]
    assert data["in_app_enabled"] is True
    assert data["email_enabled"] is False
    assert data["webhook_enabled"] is True
    assert data["minimum_severity"] == "warning"
    assert data["alert_types"] == ["portfolio_loss", "price_move"]


def test_update_preferences_invalid_severity(client):
    """Verify rejection of invalid severity value."""
    token = _get_auth_token(client, "user_invalid_sev@example.com")
    resp = client.put(
        "/api/v1/notifications/preferences",
        json={"minimum_severity": "super_critical_urgent"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "Invalid minimum_severity" in resp.get_json()["error"]["message"]


def test_preferences_unauthenticated(client):
    """Verify unauthenticated request is rejected."""
    resp = client.get("/api/v1/notifications/preferences")
    assert resp.status_code == 401


def test_preferences_multi_tenant_isolation(client):
    """Verify User A cannot see or mutate User B's preferences."""
    token_a = _get_auth_token(client, "pref_user_a@example.com")
    token_b = _get_auth_token(client, "pref_user_b@example.com")

    # User A sets minimum_severity to critical
    client.put(
        "/api/v1/notifications/preferences",
        json={"minimum_severity": "critical"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B fetches their own preferences (should remain default 'info')
    resp_b = client.get(
        "/api/v1/notifications/preferences",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b.get_json()["data"]["preferences"]["minimum_severity"] == "info"
