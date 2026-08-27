import pytest
from app.services.embedding_service import EmbeddingService


def test_embedding_service_model_default_and_validation():
    """Verify EmbeddingService defaults to gemini-embedding-2 and validates input."""
    service = EmbeddingService(api_key="test-api-key")
    assert service.model is None  # Resolves dynamically to gemini-embedding-2
    assert service.dimension == 768

    # Empty string validation
    with pytest.raises(ValueError, match="cannot be empty"):
        service.generate_embedding("")

    with pytest.raises(ValueError, match="cannot be empty"):
        service.generate_embedding("   ")


def test_embedding_service_missing_api_key():
    """Verify clean failure when GEMINI_API_KEY is not configured."""
    service = EmbeddingService(api_key="")
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is not configured"):
        service.generate_embedding("Test content")
