import pytest
from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService


class MockEmbeddingService(EmbeddingService):
    def __init__(self):
        super().__init__(api_key="mock-key")

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Input text for embedding cannot be empty.")
        # Deterministic mock 768-dimensional float vector
        return [0.05] * 768


class MockSupabaseQuery:
    def __init__(self, data_store):
        self.data_store = data_store
        self._filters = []
        self._limit = None
        self._is_delete = False
        self._insert_record = None

    def select(self, fields="*"):
        return self

    def eq(self, column, value):
        self._filters.append((column, value))
        return self

    def order(self, column, desc=False):
        return self

    def limit(self, count):
        self._limit = count
        return self

    def insert(self, record):
        self._insert_record = record
        return self

    def delete(self):
        self._is_delete = True
        return self

    def execute(self):
        import uuid
        from datetime import datetime, timezone

        if self._insert_record is not None:
            now_iso = datetime.now(timezone.utc).isoformat()
            item = {
                "id": str(uuid.uuid4()),
                "created_at": now_iso,
                "updated_at": now_iso,
                **self._insert_record,
            }
            self.data_store.append(item)

            class InsertRes:
                data = [item]

            return InsertRes()

        matched = list(self.data_store)
        for col, val in self._filters:
            matched = [m for m in matched if m.get(col) == val]

        if self._is_delete:
            for item in matched:
                if item in self.data_store:
                    self.data_store.remove(item)

        if self._limit is not None:
            matched = matched[: self._limit]

        class QueryRes:
            data = matched

        return QueryRes()


class MockSupabaseClient:
    def __init__(self):
        self.storage = []

    def table(self, name):
        return MockSupabaseQuery(self.storage)

    def rpc(self, fn_name, params):
        p_user_id = params.get("p_user_id")
        p_threshold = params.get("p_match_threshold", 0.5)
        p_count = params.get("p_match_count", 5)
        p_type = params.get("p_memory_type")

        results = []
        for item in self.storage:
            if item.get("user_id") == p_user_id:
                if p_type is None or item.get("memory_type") == p_type:
                    res_item = dict(item)
                    res_item["similarity"] = 0.95
                    results.append(res_item)

        results = [r for r in results if r["similarity"] >= p_threshold][:p_count]

        class RpcRes:
            data = results

        return type("RpcExecutor", (), {"execute": lambda self=None: RpcRes()})()


def test_embedding_service_validation():
    """Verify EmbeddingService validates empty text input."""
    service = EmbeddingService(api_key="test-key")
    with pytest.raises(ValueError, match="cannot be empty"):
        service.generate_embedding("")


def test_memory_service_create_and_duplicate_prevention():
    """Verify MemoryService creates memories and handles duplicate contents."""
    mock_supabase = MockSupabaseClient()
    mock_embed = MockEmbeddingService()
    service = MemoryService(supabase_client=mock_supabase, embedding_service=mock_embed)

    # 1. Create memory
    mem1 = service.create_memory(
        user_id=1,
        content="I prefer technology and semiconductor investments.",
        memory_type="preference",
        importance="high",
        metadata={"topic": "semiconductors"},
    )
    assert mem1["user_id"] == 1
    assert mem1["content"] == "I prefer technology and semiconductor investments."
    assert mem1["importance"] == "high"
    assert "embedding" not in mem1

    # 2. Attempt duplicate creation for same user
    mem2 = service.create_memory(
        user_id=1,
        content="I prefer technology and semiconductor investments.",
    )
    assert mem2["id"] == mem1["id"]
    assert len(mock_supabase.storage) == 1


def test_memory_service_input_validation():
    """Verify validation on user ID, memory type, and importance."""
    service = MemoryService(supabase_client=MockSupabaseClient(), embedding_service=MockEmbeddingService())

    # Invalid user_id
    with pytest.raises(ValueError, match="Valid user ID"):
        service.create_memory(user_id=0, content="Test")

    # Invalid memory_type
    with pytest.raises(ValueError, match="Invalid memory type"):
        service.create_memory(user_id=1, content="Test", memory_type="invalid_type")

    # Invalid importance
    with pytest.raises(ValueError, match="Invalid importance"):
        service.create_memory(user_id=1, content="Test", importance="super_critical")


def test_memory_service_search_and_delete():
    """Verify search and delete behavior in MemoryService."""
    mock_supabase = MockSupabaseClient()
    service = MemoryService(supabase_client=mock_supabase, embedding_service=MockEmbeddingService())

    mem = service.create_memory(user_id=1, content="Tech focus")

    # Search
    results = service.search_memories(user_id=1, query="Tech", limit=5)
    assert len(results) == 1
    assert results[0]["similarity"] == 0.95

    # Delete with correct user_id
    deleted = service.delete_memory(user_id=1, memory_id=mem["id"])
    assert deleted is True

    # Delete non-existent
    deleted_again = service.delete_memory(user_id=1, memory_id=mem["id"])
    assert deleted_again is False
