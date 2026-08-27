import pytest
from app.services.memory_service import MemoryService
from tests.unit.test_memory_service import MockEmbeddingService, MockSupabaseClient


@pytest.fixture(autouse=True)
def inject_mock_memory_service(app):
    """Injects a mock MemoryService into app.extensions for fast, isolated testing."""
    mock_supabase = MockSupabaseClient()
    mock_embedding = MockEmbeddingService()
    service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embedding)
    app.extensions["memory_service"] = service
    yield service


def test_create_memory_authenticated(client):
    """Verify authenticated user can create a memory record."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "mem_user@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    payload = {
        "content": "I prefer tech companies with strong moat and high free cash flow.",
        "memory_type": "strategy",
        "importance": "high",
        "metadata": {"sector": "technology"},
    }
    res = client.post(
        "/api/v1/memory",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    memory = data["data"]["memory"]
    assert memory["content"] == payload["content"]
    assert memory["memory_type"] == "strategy"
    assert memory["importance"] == "high"
    assert memory["metadata"]["sector"] == "technology"
    assert "embedding" not in memory


def test_create_memory_unauthenticated(client):
    """Verify unauthenticated request is rejected with 401."""
    res = client.post("/api/v1/memory", json={"content": "Some thought"})
    assert res.status_code == 401


def test_create_memory_validation_errors(client):
    """Verify input validation on memory creation."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "val_user@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    # Empty content
    res1 = client.post(
        "/api/v1/memory",
        json={"content": ""},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res1.status_code == 400

    # Invalid memory_type
    res2 = client.post(
        "/api/v1/memory",
        json={"content": "Valid content", "memory_type": "invalid_type"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res2.status_code == 400
    assert "Invalid memory type" in res2.get_json()["error"]["message"]

    # Invalid importance
    res3 = client.post(
        "/api/v1/memory",
        json={"content": "Valid content", "importance": "critical"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res3.status_code == 400
    assert "Invalid importance" in res3.get_json()["error"]["message"]


def test_create_memory_duplicate_prevention(client):
    """Verify exact duplicate memory submission returns existing record."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "dup_mem@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    payload = {"content": "Duplicate preference statement"}
    res1 = client.post("/api/v1/memory", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 201
    mem1_id = res1.get_json()["data"]["memory"]["id"]

    res2 = client.post("/api/v1/memory", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 201
    mem2_id = res2.get_json()["data"]["memory"]["id"]

    assert mem1_id == mem2_id


def test_list_and_search_memories(client):
    """Verify listing and semantic search endpoints."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "searcher@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    client.post(
        "/api/v1/memory",
        json={"content": "NVDA is my core semiconductor holding"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List
    list_res = client.get("/api/v1/memory", headers={"Authorization": f"Bearer {token}"})
    assert list_res.status_code == 200
    assert list_res.get_json()["data"]["count"] == 1

    # Search without query -> 400
    bad_search = client.get("/api/v1/memory/search", headers={"Authorization": f"Bearer {token}"})
    assert bad_search.status_code == 400

    # Valid Search
    search_res = client.get(
        "/api/v1/memory/search?q=semiconductor",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert search_res.status_code == 200
    data = search_res.get_json()["data"]
    assert data["count"] == 1
    assert data["results"][0]["similarity"] >= 0.5


def test_delete_memory(client):
    """Verify memory deletion endpoint."""
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": "deleter@example.com", "password": "Password123!"},
    )
    token = reg.get_json()["data"]["access_token"]

    create_res = client.post(
        "/api/v1/memory",
        json={"content": "Temporary note"},
        headers={"Authorization": f"Bearer {token}"},
    )
    mem_id = create_res.get_json()["data"]["memory"]["id"]

    # Delete existing
    del_res = client.delete(
        f"/api/v1/memory/{mem_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert del_res.get_json()["data"]["deleted"] is True

    # Delete non-existent -> 404
    del_again = client.delete(
        f"/api/v1/memory/{mem_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_again.status_code == 404


def test_multi_user_memory_isolation(client):
    """
    CRITICAL SECURITY TEST:
    Verify strict user memory isolation. User A can never search, list, or delete User B's memories.
    """
    # 1. Register User A
    res_a = client.post(
        "/api/v1/auth/register",
        json={"email": "user_a_mem@example.com", "password": "Password123!"},
    )
    token_a = res_a.get_json()["data"]["access_token"]

    # 2. Register User B
    res_b = client.post(
        "/api/v1/auth/register",
        json={"email": "user_b_mem@example.com", "password": "Password123!"},
    )
    token_b = res_b.get_json()["data"]["access_token"]

    # 3. User A creates Memory A1, A2
    client.post(
        "/api/v1/memory",
        json={"content": "User A prefers tech and high growth"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    client.post(
        "/api/v1/memory",
        json={"content": "User A holds AAPL and MSFT"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # 4. User B creates Memory B1, B2
    res_b1 = client.post(
        "/api/v1/memory",
        json={"content": "User B prefers high dividend value stocks"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    mem_b1_id = res_b1.get_json()["data"]["memory"]["id"]

    client.post(
        "/api/v1/memory",
        json={"content": "User B avoids high beta tech stocks"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # 5. User A searches: must contain ONLY User A's memories
    search_a = client.get(
        "/api/v1/memory/search?q=stocks",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    results_a = search_a.get_json()["data"]["results"]
    assert len(results_a) == 2
    for r in results_a:
        assert "User A" in r["content"]
        assert "User B" not in r["content"]

    # 6. User B searches: must contain ONLY User B's memories
    search_b = client.get(
        "/api/v1/memory/search?q=stocks",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    results_b = search_b.get_json()["data"]["results"]
    assert len(results_b) == 2
    for r in results_b:
        assert "User B" in r["content"]
        assert "User A" not in r["content"]

    # 7. User A attempts to DELETE User B's memory (mem_b1_id)
    tamper_del = client.delete(
        f"/api/v1/memory/{mem_b1_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert tamper_del.status_code == 404

    # 8. Verify User B's memory was untouched and remains intact
    list_b = client.get("/api/v1/memory", headers={"Authorization": f"Bearer {token_b}"})
    mem_b_ids = [m["id"] for m in list_b.get_json()["data"]["memories"]]
    assert mem_b1_id in mem_b_ids
