"""Prompt templates for the grounded agent."""

SYSTEM_PROMPT = """\
You are an internal support assistant for a company that uses a platform called Atlas.
Your job is to answer employee questions accurately using ONLY the context provided below.

Rules:
1. ONLY use information from the provided context to answer. Never use outside knowledge.
2. Cite your sources inline using [source_id] format (e.g., [service-accounts], [TK-002]).
3. If the context does not contain enough information to answer the question confidently, \
respond with exactly: "I don't have enough information to answer this question. \
Please contact your team lead or post in the relevant Slack channel for help."
4. Be concise and direct. Use bullet points or numbered steps when appropriate.
5. If multiple sources are relevant, synthesize them into a single coherent answer.
"""


def build_context_block(search_results) -> str:
    """Format retrieved chunks into a context block for the prompt."""
    parts = []
    for i, result in enumerate(search_results, 1):
        source_label = f"[{result.source_id}]"
        type_label = "Knowledge Base" if result.source_type == "knowledge_base" else "Past Ticket"
        parts.append(
            f"--- Source {i} {source_label} ({type_label}, relevance: {result.score:.2f}) ---\n"
            f"{result.text}\n"
        )
    return "\n".join(parts)


def build_user_prompt(question: str, search_results) -> str:
    """Build the full user prompt with context and question."""
    context = build_context_block(search_results)
    return (
        f"Context:\n{context}\n"
        f"---\n\n"
        f"Question: {question}\n\n"
        f"Answer the question using only the context above. Cite sources with [source_id]."
    )
