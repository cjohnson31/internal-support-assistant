"""Retrieve relevant chunks from the vector store for a query."""

from __future__ import annotations

from dataclasses import dataclass

from src.config import settings
from src.ingest.pipeline import get_chroma_collection
from src.llm import embed


@dataclass
class SearchResult:
    """A retrieved chunk with its relevance score."""
    text: str
    source_id: str
    source_title: str
    source_type: str
    distance: float  # lower = more similar (cosine distance)

    @property
    def score(self) -> float:
        """Similarity score (1 - distance). Higher = more relevant."""
        return 1.0 - self.distance


def search(query: str, top_k: int | None = None) -> list[SearchResult]:
    """Embed the query and retrieve the top-k most relevant chunks."""
    k = top_k or settings.retrieval_top_k
    collection = get_chroma_collection()

    query_embedding = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    search_results: list[SearchResult] = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        search_results.append(SearchResult(
            text=doc,
            source_id=meta["source_id"],
            source_title=meta["source_title"],
            source_type=meta["source_type"],
            distance=dist,
        ))

    return search_results
