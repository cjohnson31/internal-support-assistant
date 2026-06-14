"""Answer generation pipeline: retrieve → prompt → generate → confidence gate."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent.prompts import SYSTEM_PROMPT, build_user_prompt
from src.config import settings
from src.llm import complete
from src.retrieval.search import SearchResult, search


REFUSAL_PREFIX = "I don't have enough information"


@dataclass
class Answer:
    """A generated answer with its sources and confidence info."""
    question: str
    text: str
    sources: list[SearchResult]
    top_score: float
    refused: bool

    @property
    def source_ids(self) -> list[str]:
        """Unique source IDs from retrieved chunks."""
        seen = set()
        ids = []
        for s in self.sources:
            if s.source_id not in seen:
                seen.add(s.source_id)
                ids.append(s.source_id)
        return ids


def generate_answer(question: str, api_key: str | None = None) -> Answer:
    """Run the full RAG pipeline: retrieve → prompt → generate → confidence gate.

    If api_key is provided, it's used for this request only (web UI flow).
    """
    # Step 1: Retrieve relevant chunks
    results = search(question)

    # Step 2: Confidence gate — if best retrieval score is too low, refuse
    top_score = results[0].score if results else 0.0

    if top_score < settings.confidence_threshold:
        return Answer(
            question=question,
            text=(
                "I don't have enough information to answer this question. "
                "Please contact your team lead or post in the relevant Slack channel for help."
            ),
            sources=results,
            top_score=top_score,
            refused=True,
        )

    # Step 3: Build prompt with retrieved context
    user_prompt = build_user_prompt(question, results)

    # Step 4: Generate answer
    response_text = complete(user_prompt, system=SYSTEM_PROMPT, api_key=api_key)

    # Step 5: Check if the model itself decided to refuse
    refused = response_text.startswith(REFUSAL_PREFIX)

    return Answer(
        question=question,
        text=response_text,
        sources=results,
        top_score=top_score,
        refused=refused,
    )
