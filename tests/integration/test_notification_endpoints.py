def _get_auth_token(client, email: str = "ep_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_create_and_list_endpoints(client):
    """Verify creating and listing webhook endpoints without secret leakage."""
    token = _get_auth_token(client, "user_ep_create@example.com")

    # Create webhook endpoint with secret
    resp = client.post(
        "/api/v1/notifications/endpoints",
        json={
            "endpoint_url": "https://webhook.site/test-aira-123",
            "channel": "webhook",
            "secret_key": "my_secret_signing_key",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    ep_data = resp.get_json()["data"]["endpoint"]
    assert ep_data["endpoint_url"] == "https://webhook.site/test-aira-123"
    assert ep_data["has_secret"] is True
    assert "secret_key" not in ep_data

    # List endpoints
    list_resp = client.get(
        "/api/v1/notifications/endpoints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    endpoints = list_resp.get_json()["data"]["endpoints"]
    assert len(endpoints) == 1
    assert endpoints[0]["endpoint_url"] == "https://webhook.site/test-aira-123"


def test_create_endpoint_ssrf_rejection(client):
    """Verify rejection of dangerous schemes and internal IP ranges."""
    token = _get_auth_token(client, "user_ep_ssrf@example.com")

    # Rejection of localhost
    resp = client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://localhost:9000/webhook"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400
    assert "Invalid endpoint URL" in resp.get_json()["error"]["message"]

    # Rejection of loopback IP
    resp2 = client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://127.0.0.1/webhook"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 400

    # Rejection of private IP
    resp3 = client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://10.0.0.1/webhook"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp3.status_code == 400


def test_update_and_delete_endpoint(client):
    """Verify endpoint update and deletion."""
    token = _get_auth_token(client, "user_ep_mod@example.com")

    create_resp = client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://api.example.com/alerts/v1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    ep_id = create_resp.get_json()["data"]["endpoint"]["id"]

    # Update endpoint
    update_resp = client.put(
        f"/api/v1/notifications/endpoints/{ep_id}",
        json={"is_enabled": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()["data"]["endpoint"]["is_enabled"] is False

    # Delete endpoint
    del_resp = client.delete(
        f"/api/v1/notifications/endpoints/{ep_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 200

    # Verify deleted
    get_resp = client.get(
        "/api/v1/notifications/endpoints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert len(get_resp.get_json()["data"]["endpoints"]) == 0


def test_endpoint_multi_tenant_isolation(client):
    """Verify User A cannot access or mutate User B's endpoint (returns 404)."""
    token_a = _get_auth_token(client, "ep_user_a@example.com")
    token_b = _get_auth_token(client, "ep_user_b@example.com")

    # User A creates endpoint
    resp_a = client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://api.example.com/a/webhook"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    ep_id_a = resp_a.get_json()["data"]["endpoint"]["id"]

    # User B attempts to update User A's endpoint -> 404
    resp_b_put = client.put(
        f"/api/v1/notifications/endpoints/{ep_id_a}",
        json={"is_enabled": False},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b_put.status_code == 404

    # User B attempts to delete User A's endpoint -> 404
    resp_b_del = client.delete(
        f"/api/v1/notifications/endpoints/{ep_id_a}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b_del.status_code == 404
