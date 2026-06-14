"""Load documents from the knowledge base and ticket history."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest.chunker import Chunk, chunk_markdown, chunk_ticket

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_knowledge_base() -> list[Chunk]:
    """Load and chunk all markdown files from data/knowledge_base/."""
    kb_dir = DATA_DIR / "knowledge_base"
    chunks: list[Chunk] = []

    for md_file in sorted(kb_dir.glob("*.md")):
        source_id = md_file.stem  # e.g. "service-accounts"
        text = md_file.read_text(encoding="utf-8")
        # Extract title from first heading, or fall back to filename
        title = source_id.replace("-", " ").title()
        for line in text.split("\n"):
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break
        chunks.extend(chunk_markdown(text, source_id, title))

    return chunks


def load_tickets() -> list[Chunk]:
    """Load and chunk all tickets from data/tickets/."""
    tickets_dir = DATA_DIR / "tickets"
    chunks: list[Chunk] = []

    for json_file in sorted(tickets_dir.glob("*.json")):
        tickets = json.loads(json_file.read_text(encoding="utf-8"))
        for ticket in tickets:
            chunks.append(chunk_ticket(ticket))

    return chunks


def load_all() -> list[Chunk]:
    """Load everything and return a flat list of chunks."""
    kb = load_knowledge_base()
    tickets = load_tickets()
    print(f"Loaded {len(kb)} knowledge base chunks + {len(tickets)} ticket chunks = {len(kb) + len(tickets)} total")
    return kb + tickets
