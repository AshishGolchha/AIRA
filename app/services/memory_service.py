from flask import current_app, has_app_context
from supabase import Client, create_client

from app.services.embedding_service import EmbeddingService

ALLOWED_MEMORY_TYPES = {
    "preference",
    "goal",
    "strategy",
    "belief",
    "context",
    "conversation",
}

ALLOWED_IMPORTANCE_LEVELS = {"low", "medium", "high"}


def _sanitize_memory_record(record: dict) -> dict:
    """Removes raw vector embeddings from returned memory dictionaries."""
    return {
        "id": record.get("id"),
        "user_id": record.get("user_id"),
        "content": record.get("content"),
        "memory_type": record.get("memory_type"),
        "importance": record.get("importance"),
        "metadata": record.get("metadata") or {},
        "created_at": record.get("created_at"),
        "updated_at": record.get("updated_at"),
        **({"similarity": record.get("similarity")} if "similarity" in record else {}),
    }


class MemoryService:
    """Manages persistent semantic user memories via Supabase and Gemini embeddings."""

    def __init__(
        self,
        supabase_client: Client | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self._supabase = supabase_client
        self.embedding_service = embedding_service or EmbeddingService()

    def _get_supabase_client(self) -> Client:
        if self._supabase:
            return self._supabase
        url = None
        key = None
        if has_app_context():
            url = current_app.config.get("SUPABASE_URL")
            key = current_app.config.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            import os
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError(
                "Supabase configuration missing. SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required."
            )
        return create_client(url, key)

    def create_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str = "preference",
        importance: str = "medium",
        metadata: dict | None = None,
    ) -> dict:
        """Stores a new user memory and its vector embedding in Supabase."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid user ID is required.")

        if not content or not isinstance(content, str) or not content.strip():
            raise ValueError("Memory content cannot be empty.")

        clean_content = content.strip()
        if len(clean_content) > 5000:
            raise ValueError("Memory content cannot exceed 5000 characters.")

        if memory_type not in ALLOWED_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type '{memory_type}'. Allowed: {sorted(ALLOWED_MEMORY_TYPES)}"
            )

        if importance not in ALLOWED_IMPORTANCE_LEVELS:
            raise ValueError(
                f"Invalid importance '{importance}'. Allowed: {sorted(ALLOWED_IMPORTANCE_LEVELS)}"
            )

        clean_metadata = metadata if isinstance(metadata, dict) else {}
        client = self._get_supabase_client()

        # Exact duplicate prevention for this specific user
        existing = (
            client.table("user_memories")
            .select("id, user_id, content, memory_type, importance, metadata, created_at, updated_at")
            .eq("user_id", user_id)
            .eq("content", clean_content)
            .limit(1)
            .execute()
        )
        if existing.data:
            return _sanitize_memory_record(existing.data[0])

        embedding = self.embedding_service.generate_embedding(clean_content)

        record = {
            "user_id": user_id,
            "content": clean_content,
            "embedding": embedding,
            "memory_type": memory_type,
            "importance": importance,
            "metadata": clean_metadata,
        }

        res = client.table("user_memories").insert(record).execute()
        if not res.data:
            raise RuntimeError("Failed to insert memory record into Supabase.")

        return _sanitize_memory_record(res.data[0])

    def search_memories(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
        threshold: float | None = None,
        memory_type: str | None = None,
    ) -> list[dict]:
        """Performs semantic vector similarity search strictly scoped to the user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid user ID is required.")

        if not query or not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if memory_type and memory_type not in ALLOWED_MEMORY_TYPES:
            raise ValueError(f"Invalid memory type filter '{memory_type}'.")

        bounded_limit = min(max(1, limit), 50)
        min_threshold = (
            threshold
            if threshold is not None
            else (
                current_app.config.get("MEMORY_SIMILARITY_THRESHOLD", 0.5)
                if has_app_context()
                else 0.5
            )
        )

        query_embedding = self.embedding_service.generate_embedding(query.strip())
        client = self._get_supabase_client()

        params = {
            "p_user_id": user_id,
            "p_embedding": query_embedding,
            "p_match_threshold": min_threshold,
            "p_match_count": bounded_limit,
            "p_memory_type": memory_type,
        }

        res = client.rpc("match_user_memories", params).execute()
        return [_sanitize_memory_record(row) for row in (res.data or [])]

    def list_memories(
        self,
        user_id: int,
        limit: int = 20,
        memory_type: str | None = None,
    ) -> list[dict]:
        """Lists recent memories for the user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid user ID is required.")

        bounded_limit = min(max(1, limit), 100)
        client = self._get_supabase_client()

        query = (
            client.table("user_memories")
            .select("id, user_id, content, memory_type, importance, metadata, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(bounded_limit)
        )

        if memory_type:
            if memory_type not in ALLOWED_MEMORY_TYPES:
                raise ValueError(f"Invalid memory type filter '{memory_type}'.")
            query = query.eq("memory_type", memory_type)

        res = query.execute()
        return [_sanitize_memory_record(row) for row in (res.data or [])]

    def delete_memory(self, user_id: int, memory_id: str) -> bool:
        """Deletes a memory record belonging strictly to the user."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid user ID is required.")

        if not memory_id or not isinstance(memory_id, str):
            raise ValueError("Valid memory ID is required.")

        client = self._get_supabase_client()
        res = (
            client.table("user_memories")
            .delete()
            .eq("id", memory_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(res.data)
