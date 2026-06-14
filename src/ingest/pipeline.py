"""Ingestion pipeline: load → chunk → embed → upsert to vector store."""

from __future__ import annotations

import chromadb

from src.config import settings
from src.ingest.loader import load_all
from src.llm import embed


def get_chroma_collection() -> chromadb.Collection:
    """Get or create the Chroma collection."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(
        name="support_docs",
        metadata={"hnsw:space": "cosine"},
    )


def ingest():
    """Run the full ingestion pipeline."""
    chunks = load_all()
    collection = get_chroma_collection()

    # Embed in batches to avoid memory issues
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.text for c in batch]
        embeddings = embed(texts)

        collection.upsert(
            ids=[f"{c.source_id}_{c.chunk_index}" for c in batch],
            documents=texts,
            embeddings=embeddings,
            metadatas=[
                {
                    "source_id": c.source_id,
                    "source_title": c.source_title,
                    "source_type": c.source_type,
                    "chunk_index": c.chunk_index,
                }
                for c in batch
            ],
        )
        print(f"  Upserted batch {i // batch_size + 1} ({len(batch)} chunks)")

    print(f"Ingestion complete. Collection has {collection.count()} chunks.")
