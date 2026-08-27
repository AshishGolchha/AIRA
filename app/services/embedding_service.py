from flask import current_app
from google import genai


class EmbeddingService:
    """Generates vector embeddings using Google Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key
        self.model = model

    def _get_client(self) -> genai.Client:
        key = self.api_key or current_app.config.get("GEMINI_API_KEY") or ""
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        return genai.Client(api_key=key)

    def generate_embedding(self, text: str) -> list[float]:
        """Generates a float embedding vector for input text."""
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Input text for embedding cannot be empty.")

        client = self._get_client()
        model_name = (
            self.model
            or current_app.config.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        )
        response = client.models.embed_content(
            model=model_name,
            contents=text.strip(),
        )
        if not response.embeddings or not response.embeddings[0].values:
            raise RuntimeError("Failed to generate embedding from Gemini API.")

        return list(response.embeddings[0].values)
