"""Provider-agnostic LLM + embeddings wrapper.

Backed by Anthropic (Claude) for generation and sentence-transformers for embeddings.
Swap the implementation here without touching the rest of the codebase.
"""

from __future__ import annotations

import anthropic

from src.config import settings

_anthropic_client: anthropic.Anthropic | None = None
_embed_model = None


def _client() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=settings.llm_api_key)
    return _anthropic_client


def _embedder():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(settings.embedding_model)
    return _embed_model


def complete(prompt: str, system: str = "", model: str | None = None) -> str:
    """Send a prompt and return the text completion."""
    response = _client().messages.create(
        model=model or settings.llm_model,
        max_tokens=1024,
        system=system or "You are a helpful assistant.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def embed(texts: list[str]) -> list[list[float]]:
    """Return embedding vectors for a list of texts."""
    vectors = _embedder().encode(texts, convert_to_numpy=True)
    return vectors.tolist()
