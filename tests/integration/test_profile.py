def test_get_profile_authenticated(client):
    """Verify authenticated user can retrieve their profile."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "prof_user@example.com", "password": "Password123!", "display_name": "Alex"},
    )
    token = reg.get_json()["data"]["access_token"]

    res = client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    profile = data["data"]["profile"]
    assert profile["display_name"] == "Alex"
    assert profile["investment_focus"] is None


def test_get_profile_unauthenticated(client):
    """Verify unauthenticated profile request is rejected with 401."""
    res = client.get("/api/v1/profile")
    assert res.status_code == 401


def test_update_profile_authenticated(client):
    """Verify authenticated user can update allowed profile fields."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "updater@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    update_payload = {
        "display_name": "Updated Name",
        "investment_focus": "Semiconductors & Cloud",
        "risk_preference": "moderate",
        "investment_horizon": "long-term",
    }
    res = client.put(
        "/api/v1/profile",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    profile = res.get_json()["data"]["profile"]
    assert profile["display_name"] == "Updated Name"
    assert profile["investment_focus"] == "Semiconductors & Cloud"
    assert profile["risk_preference"] == "moderate"
    assert profile["investment_horizon"] == "long-term"


def test_update_profile_invalid_type(client):
    """Verify invalid non-string field types in profile update return 400."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "type_check@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    res = client.put(
        "/api/v1/profile",
        json={"display_name": 12345},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "must be a string" in res.get_json()["error"]["message"]


def test_multi_user_data_isolation(client):
    """
    CRITICAL SECURITY TEST:
    Verify strict tenant data isolation between User A and User B.
    User A cannot read or mutate User B's profile, and client-supplied user IDs are ignored.
    """
    # 1. Register User A
    res_a = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_a@example.com",
            "password": "PasswordUserA123!",
            "display_name": "User A",
        },
    )
    token_a = res_a.get_json()["data"]["access_token"]
    user_a_id = res_a.get_json()["data"]["user"]["id"]

    # 2. Register User B
    res_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user_b@example.com",
            "password": "PasswordUserB123!",
            "display_name": "User B",
        },
    )
    token_b = res_b.get_json()["data"]["access_token"]
    user_b_id = res_b.get_json()["data"]["user"]["id"]

    # 3. User A updates their profile
    client.put(
        "/api/v1/profile",
        json={
            "investment_focus": "Tech & AI Growth",
            "risk_preference": "aggressive",
            "investment_horizon": "long-term",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # 4. User B updates their profile
    client.put(
        "/api/v1/profile",
        json={
            "investment_focus": "Value & High Dividends",
            "risk_preference": "conservative",
            "investment_horizon": "short-term",
        },
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # 5. Verify User A reads only User A's data
    get_a = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token_a}"})
    assert get_a.status_code == 200
    profile_a = get_a.get_json()["data"]["profile"]
    assert "user_id" not in profile_a
    assert profile_a["display_name"] == "User A"
    assert profile_a["investment_focus"] == "Tech & AI Growth"
    assert profile_a["risk_preference"] == "aggressive"

    # 6. Verify User B reads only User B's data
    get_b = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b.status_code == 200
    profile_b = get_b.get_json()["data"]["profile"]
    assert "user_id" not in profile_b
    assert profile_b["display_name"] == "User B"
    assert profile_b["investment_focus"] == "Value & High Dividends"
    assert profile_b["risk_preference"] == "conservative"

    # 7. User A attempts to tamper by sending user_b_id in update payload
    tamper_res = client.put(
        "/api/v1/profile",
        json={
            "user_id": user_b_id,
            "investment_focus": "Malicious Tampered Focus",
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert tamper_res.status_code == 200

    # 8. Confirm User B's profile was completely unaffected
    check_b = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token_b}"})
    profile_b_post_tamper = check_b.get_json()["data"]["profile"]
    assert profile_b_post_tamper["display_name"] == "User B"
    assert profile_b_post_tamper["investment_focus"] == "Value & High Dividends"
    assert profile_b_post_tamper["investment_focus"] != "Malicious Tampered Focus"

    # 9. Confirm User A's profile only was updated
    check_a = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token_a}"})
    profile_a_post_tamper = check_a.get_json()["data"]["profile"]
    assert profile_a_post_tamper["display_name"] == "User A"
    assert profile_a_post_tamper["investment_focus"] == "Malicious Tampered Focus"
