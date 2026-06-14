"""CLI for the internal support assistant.

Usage:
    python -m src.cli ingest       # Load docs into the vector store
    python -m src.cli ask "..."    # Ask a question (full RAG pipeline)
    python -m src.cli search "..." # Retrieve raw chunks (no answer generation)
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
def cli():
    """Internal Support Assistant CLI."""
    pass


@cli.command()
def ingest():
    """Load documents into the vector store."""
    console.print("[bold blue]Starting ingestion...[/bold blue]")
    from src.ingest.pipeline import ingest as run_ingest
    run_ingest()
    console.print("[bold green]Done![/bold green]")


@cli.command()
@click.argument("question")
def ask(question: str):
    """Ask a question and get a grounded answer with citations."""
    from src.agent.answer import generate_answer

    console.print(f"\n[bold]Question:[/bold] {question}\n")

    with console.status("[bold blue]Thinking...[/bold blue]"):
        answer = generate_answer(question)

    # Display the answer
    style = "red" if answer.refused else "green"
    label = "REFUSED — Low Confidence" if answer.refused else "Answer"
    console.print(Panel(answer.text, title=label, border_style=style))

    # Display sources
    console.print(f"\n[dim]Top retrieval score: {answer.top_score:.3f}[/dim]")
    console.print("[dim]Sources used:[/dim]")
    for r in answer.sources:
        icon = "📄" if r.source_type == "knowledge_base" else "🎫"
        console.print(f"  {icon} [{r.source_id}] {r.source_title} (score: {r.score:.3f})")
    console.print()


@cli.command()
@click.argument("question")
def search(question: str):
    """Retrieve raw chunks for a question (no answer generation)."""
    from src.retrieval.search import search as do_search

    console.print(f"\n[bold]Query:[/bold] {question}\n")
    results = do_search(question)

    table = Table(title="Retrieved Chunks", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Score", width=7)
    table.add_column("Source", width=25)
    table.add_column("Type", width=8)
    table.add_column("Text", max_width=80)

    for i, r in enumerate(results, 1):
        table.add_row(
            str(i),
            f"{r.score:.3f}",
            r.source_title,
            r.source_type,
            r.text[:200] + "..." if len(r.text) > 200 else r.text,
        )

    console.print(table)


if __name__ == "__main__":
    cli()
