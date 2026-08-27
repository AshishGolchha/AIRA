from flask import current_app, has_app_context
from google import genai
from google.genai import types


class EmbeddingService:
    """Generates vector embeddings using Google Gemini API (gemini-embedding-2)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimension: int = 768,
    ):
        self.api_key = api_key
        self.model = model
        self.dimension = dimension

    def _get_client(self) -> genai.Client:
        key = self.api_key
        if not key and has_app_context():
            key = current_app.config.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        return genai.Client(api_key=key)

    def generate_embedding(self, text: str) -> list[float]:
        """Generates a 768-dimension float embedding vector for input text."""
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Input text for embedding cannot be empty.")

        client = self._get_client()
        model_name = self.model
        if not model_name and has_app_context():
            model_name = current_app.config.get(
                "GEMINI_EMBEDDING_MODEL", "gemini-embedding-2"
            )
        model_name = model_name or "gemini-embedding-2"

        dimension = self.dimension
        if has_app_context():
            dimension = int(current_app.config.get("EMBEDDING_DIMENSION", self.dimension))

        config = types.EmbedContentConfig(output_dimensionality=dimension)
        response = client.models.embed_content(
            model=model_name,
            contents=text.strip(),
            config=config,
        )
        if not response.embeddings or not response.embeddings[0].values:
            raise RuntimeError("Failed to generate embedding from Gemini API.")

        return list(response.embeddings[0].values)
