"""Eval harness runner.

Runs the RAG pipeline against the test set, scores each case,
and writes a dated report.

Usage:
    python -m evals.run_evals
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from evals.metrics import (
    answer_correctness,
    groundedness,
    refusal_accuracy,
    retrieval_hit_rate,
)
from src.agent.answer import generate_answer

console = Console()
EVALS_DIR = Path(__file__).resolve().parent
REPORTS_DIR = EVALS_DIR / "reports"


def load_testset() -> list[dict]:
    """Load the test set from YAML."""
    testset_path = EVALS_DIR / "testset.yaml"
    with open(testset_path) as f:
        return yaml.safe_load(f)


def run_single(case: dict) -> dict:
    """Run the pipeline on one test case and score it."""
    question = case["question"]
    key_facts = case.get("key_facts", [])
    expected_sources = case.get("expected_source_ids", [])
    should_refuse = case.get("should_refuse", False)

    # Run the RAG pipeline
    answer = generate_answer(question)

    # Collect retrieved source IDs
    retrieved_ids = [r.source_id for r in answer.sources]
    retrieved_texts = [r.text for r in answer.sources]

    # Score all metrics
    hit_rate = retrieval_hit_rate(retrieved_ids, expected_sources)
    refusal = refusal_accuracy(answer.text, answer.refused, should_refuse)

    # Only run LLM-as-judge on non-refused, answerable questions
    if should_refuse or answer.refused:
        correctness = None
        grounded = None
    else:
        correctness = answer_correctness(question, answer.text, key_facts)
        grounded = groundedness(answer.text, retrieved_texts)

    return {
        "id": case["id"],
        "question": question,
        "should_refuse": should_refuse,
        "did_refuse": answer.refused,
        "top_score": answer.top_score,
        "answer_preview": answer.text[:150],
        "retrieval_hit_rate": hit_rate,
        "refusal_accuracy": refusal,
        "correctness": correctness,
        "groundedness": grounded,
        "retrieved_sources": retrieved_ids,
        "expected_sources": expected_sources,
    }


def aggregate(results: list[dict]) -> dict:
    """Compute aggregate scores from individual results."""
    n = len(results)
    answerable = [r for r in results if not r["should_refuse"]]
    refusals = [r for r in results if r["should_refuse"]]

    correctness_scores = [r["correctness"] for r in answerable if r["correctness"] is not None]
    groundedness_scores = [r["groundedness"] for r in answerable if r["groundedness"] is not None]

    return {
        "total_cases": n,
        "answerable_cases": len(answerable),
        "refusal_cases": len(refusals),
        "retrieval_hit_rate": sum(r["retrieval_hit_rate"] for r in results) / n if n else 0,
        "refusal_accuracy": sum(r["refusal_accuracy"] for r in results) / n if n else 0,
        "avg_correctness": sum(correctness_scores) / len(correctness_scores) if correctness_scores else 0,
        "avg_groundedness": sum(groundedness_scores) / len(groundedness_scores) if groundedness_scores else 0,
        "answerable_refusal_accuracy": (
            sum(r["refusal_accuracy"] for r in answerable) / len(answerable) if answerable else 0
        ),
        "oos_refusal_accuracy": (
            sum(r["refusal_accuracy"] for r in refusals) / len(refusals) if refusals else 0
        ),
    }


def write_report(results: list[dict], agg: dict) -> Path:
    """Write a dated markdown report."""
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_path = REPORTS_DIR / f"eval_report_{timestamp}.md"

    lines = [
        f"# Eval Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Aggregate Scores",
        "",
        "| Metric | Score |",
        "|--------|-------|",
        f"| Retrieval Hit-Rate@5 | {agg['retrieval_hit_rate']:.1%} |",
        f"| Refusal Accuracy (overall) | {agg['refusal_accuracy']:.1%} |",
        f"| Refusal Accuracy (answerable) | {agg['answerable_refusal_accuracy']:.1%} |",
        f"| Refusal Accuracy (out-of-scope) | {agg['oos_refusal_accuracy']:.1%} |",
        f"| Avg Correctness (1-5) | {agg['avg_correctness']:.2f} |",
        f"| Avg Groundedness (1-5) | {agg['avg_groundedness']:.2f} |",
        "",
        f"Total cases: {agg['total_cases']} "
        f"({agg['answerable_cases']} answerable, {agg['refusal_cases']} out-of-scope)",
        "",
        "## Per-Case Results",
        "",
        "| ID | Question | Hit-Rate | Refusal | Correct | Grounded | Top Score |",
        "|----|----------|----------|---------|---------|----------|-----------|",
    ]

    for r in results:
        corr = str(r["correctness"]) if r["correctness"] is not None else "—"
        grnd = str(r["groundedness"]) if r["groundedness"] is not None else "—"
        refused_marker = " ⛔" if r["did_refuse"] else ""
        lines.append(
            f"| {r['id']} "
            f"| {r['question'][:50]}{'...' if len(r['question']) > 50 else ''} "
            f"| {r['retrieval_hit_rate']:.0%} "
            f"| {r['refusal_accuracy']:.0%} "
            f"| {corr} "
            f"| {grnd} "
            f"| {r['top_score']:.3f}{refused_marker} |"
        )

    # Failures section
    failures = [r for r in results if r["refusal_accuracy"] < 1.0
                or (r["correctness"] is not None and r["correctness"] <= 2)]
    if failures:
        lines.extend([
            "",
            "## Failures / Low Scores",
            "",
        ])
        for r in failures:
            lines.append(f"### {r['id']}: {r['question']}")
            lines.append(f"- **Should refuse:** {r['should_refuse']}, **Did refuse:** {r['did_refuse']}")
            lines.append(f"- **Correctness:** {r['correctness']}, **Groundedness:** {r['groundedness']}")
            lines.append(f"- **Answer preview:** {r['answer_preview']}")
            lines.append(f"- **Retrieved:** {r['retrieved_sources']}")
            lines.append(f"- **Expected:** {r['expected_sources']}")
            lines.append("")

    lines.extend(["", "---", f"_Generated by eval harness at {timestamp}_"])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main():
    """Run the full eval suite."""
    testset = load_testset()
    console.print(f"\n[bold blue]Running evals on {len(testset)} test cases...[/bold blue]\n")

    results = []
    for i, case in enumerate(testset, 1):
        label = "🚫 OOS" if case.get("should_refuse") else "✅ ANS"
        console.print(f"  [{i}/{len(testset)}] {label}  {case['id']}: {case['question'][:60]}")
        result = run_single(case)

        # Show inline pass/fail
        status_parts = []
        if result["retrieval_hit_rate"] < 1.0:
            status_parts.append("[red]retrieval miss[/red]")
        if result["refusal_accuracy"] < 1.0:
            status_parts.append("[red]refusal wrong[/red]")
        if result["correctness"] is not None and result["correctness"] <= 2:
            status_parts.append(f"[red]correctness={result['correctness']}[/red]")
        if not status_parts:
            status_parts.append("[green]pass[/green]")
        console.print(f"         → {', '.join(status_parts)}")

        results.append(result)

    # Aggregate and report
    agg = aggregate(results)

    # Print summary table
    console.print()
    table = Table(title="Eval Results Summary", show_lines=True)
    table.add_column("Metric", style="bold")
    table.add_column("Score", justify="right")
    table.add_row("Retrieval Hit-Rate@5", f"{agg['retrieval_hit_rate']:.1%}")
    table.add_row("Refusal Accuracy (overall)", f"{agg['refusal_accuracy']:.1%}")
    table.add_row("  ↳ Answerable (should NOT refuse)", f"{agg['answerable_refusal_accuracy']:.1%}")
    table.add_row("  ↳ Out-of-scope (SHOULD refuse)", f"{agg['oos_refusal_accuracy']:.1%}")
    table.add_row("Avg Correctness (1–5)", f"{agg['avg_correctness']:.2f}")
    table.add_row("Avg Groundedness (1–5)", f"{agg['avg_groundedness']:.2f}")
    console.print(table)

    # Write report
    report_path = write_report(results, agg)
    console.print(f"\n[bold green]Report written to:[/bold green] {report_path}\n")

    # Also save raw results as JSON for programmatic use
    json_path = report_path.with_suffix(".json")
    json_path.write_text(json.dumps({"aggregate": agg, "results": results}, indent=2))
    console.print(f"[dim]Raw results: {json_path}[/dim]\n")


if __name__ == "__main__":
    main()
