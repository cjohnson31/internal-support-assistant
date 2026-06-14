"""Split documents into chunks with metadata for embedding and retrieval."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """A chunk of text with its source metadata."""
    text: str
    source_id: str    # e.g. "service-accounts" or "TK-042"
    source_title: str # human-readable title
    source_type: str  # "knowledge_base" or "ticket"
    chunk_index: int  # position within the source document


def chunk_markdown(text: str, source_id: str, source_title: str, max_chars: int = 800) -> list[Chunk]:
    """Split a markdown doc into chunks on heading boundaries.

    Strategy: split on '## ' headings. If a section is still longer than
    max_chars, split it further on double-newlines (paragraphs).

    Each chunk gets a contextual prefix ("Document: <title> > Section: <heading>")
    so the embedding captures what the chunk is about, not just its raw content.
    This significantly improves retrieval for tables and lists where the raw text
    is hard to match semantically.
    """
    sections = _split_on_headings(text)
    chunks: list[Chunk] = []

    for section in sections:
        # Extract section heading (if any) for the contextual prefix
        section_heading = ""
        for line in section.split("\n"):
            if line.startswith("## "):
                section_heading = line.lstrip("# ").strip()
                break
            elif line.startswith("# "):
                section_heading = line.lstrip("# ").strip()
                break

        prefix = f"Document: {source_title}"
        if section_heading:
            prefix += f" > Section: {section_heading}"
        prefix += "\n\n"

        if len(prefix + section) <= max_chars:
            chunks.append(Chunk(
                text=(prefix + section).strip(),
                source_id=source_id,
                source_title=source_title,
                source_type="knowledge_base",
                chunk_index=len(chunks),
            ))
        else:
            # Split long sections on paragraph boundaries
            paragraphs = section.split("\n\n")
            buffer = ""
            for para in paragraphs:
                if len(buffer) + len(para) > max_chars and buffer:
                    chunks.append(Chunk(
                        text=(prefix + buffer).strip(),
                        source_id=source_id,
                        source_title=source_title,
                        source_type="knowledge_base",
                        chunk_index=len(chunks),
                    ))
                    buffer = para
                else:
                    buffer = buffer + "\n\n" + para if buffer else para
            if buffer.strip():
                chunks.append(Chunk(
                    text=(prefix + buffer).strip(),
                    source_id=source_id,
                    source_title=source_title,
                    source_type="knowledge_base",
                    chunk_index=len(chunks),
                ))
    return chunks


def chunk_ticket(ticket: dict) -> Chunk:
    """Turn a single ticket dict into one chunk."""
    text = (
        f"Ticket {ticket['id']}: {ticket['title']}\n"
        f"Category: {ticket.get('category', 'general')}\n"
        f"Problem: {ticket['description']}\n"
        f"Resolution: {ticket['resolution']}"
    )
    return Chunk(
        text=text,
        source_id=ticket["id"],
        source_title=ticket["title"],
        source_type="ticket",
        chunk_index=0,
    )


def _split_on_headings(text: str) -> list[str]:
    """Split markdown text on ## headings, keeping the heading with its section."""
    lines = text.split("\n")
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        if line.startswith("## ") and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    return [s for s in sections if s.strip()]
