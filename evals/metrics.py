"""Eval metrics: retrieval hit-rate, answer correctness, groundedness, refusal accuracy.

Uses LLM-as-judge for correctness and groundedness scoring.
"""

from __future__ import annotations

from src.config import settings
from src.llm import complete


# ── Retrieval Hit-Rate ─────────────────────────────────────────────

def retrieval_hit_rate(retrieved_source_ids: list[str], expected_source_ids: list[str]) -> float:
    """Did at least one expected source appear in the retrieved chunks?

    Returns 1.0 if any expected source was retrieved, 0.0 otherwise.
    Returns 1.0 if no expected sources were specified (nothing to check).
    """
    if not expected_source_ids:
        return 1.0
    retrieved_set = set(retrieved_source_ids)
    return 1.0 if any(eid in retrieved_set for eid in expected_source_ids) else 0.0


# ── Refusal Accuracy ───────────────────────────────────────────────

def refusal_accuracy(answer_text: str, answer_refused: bool, should_refuse: bool) -> float:
    """Did the agent correctly refuse (or not refuse)?

    Returns 1.0 if behavior matches expectation, 0.0 otherwise.
    """
    if should_refuse:
        return 1.0 if answer_refused else 0.0
    else:
        return 1.0 if not answer_refused else 0.0


# ── Answer Correctness (LLM-as-Judge) ─────────────────────────────

CORRECTNESS_PROMPT = """\
You are an eval judge. Given a question, a list of key facts that a correct answer must contain, \
and the actual answer produced by an AI assistant, score the answer's correctness.

Question: {question}

Key facts the answer MUST contain:
{key_facts}

AI assistant's answer:
{answer}

Score the answer on a scale of 1-5:
1 = Completely wrong or missing all key facts
2 = Contains some relevant info but misses most key facts
3 = Contains about half the key facts
4 = Contains most key facts with minor omissions
5 = Contains all key facts accurately

Respond with ONLY a single integer (1-5), nothing else."""


def answer_correctness(question: str, answer_text: str, key_facts: list[str]) -> int:
    """Score answer correctness using LLM-as-judge. Returns 1-5."""
    if not key_facts:
        return 5  # No facts to check — vacuously correct

    facts_str = "\n".join(f"- {f}" for f in key_facts)
    prompt = CORRECTNESS_PROMPT.format(
        question=question,
        key_facts=facts_str,
        answer=answer_text,
    )

    response = complete(prompt, model=settings.judge_model)
    try:
        score = int(response.strip())
        return max(1, min(5, score))
    except ValueError:
        # If judge response isn't parseable, be conservative
        return 3


# ── Groundedness (LLM-as-Judge) ────────────────────────────────────

GROUNDEDNESS_PROMPT = """\
You are an eval judge. Given the retrieved context chunks and the AI assistant's answer, \
determine whether every claim in the answer is supported by the provided context.

Retrieved context:
{context}

AI assistant's answer:
{answer}

Score the groundedness on a scale of 1-5:
1 = Most claims are fabricated / not in the context
2 = Several unsupported claims
3 = Mix of supported and unsupported claims
4 = Mostly grounded with minor extrapolations
5 = Every claim is directly supported by the context

Respond with ONLY a single integer (1-5), nothing else."""


def groundedness(answer_text: str, retrieved_chunks: list[str]) -> int:
    """Score whether the answer is grounded in retrieved context. Returns 1-5."""
    if not retrieved_chunks:
        return 1  # No context to ground against

    context_str = "\n---\n".join(retrieved_chunks)
    prompt = GROUNDEDNESS_PROMPT.format(
        context=context_str,
        answer=answer_text,
    )

    response = complete(prompt, model=settings.judge_model)
    try:
        score = int(response.strip())
        return max(1, min(5, score))
    except ValueError:
        return 3
