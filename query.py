# MODULE: CLI entry point for health checks, retrieval commands, and privacy route inspection.
"""Command-line interface for operating the Personal AI Brain project."""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.table import Table

from src.api.privacy_router import choose_model_route
from src.common.health import collect_core_health
from src.ingestion.embedder import Embedder
from src.ingestion.vector_store import SearchResult, VectorStore

app = typer.Typer(help="Operate and inspect the Personal AI Brain project.")
console = Console()


def _fail_cli(message: str, code: int = 2) -> None:
    """Print a CLI validation error and exit with a non-zero status.

    Parameters:
        message: Human-readable validation message.
        code: Process exit status.
    """
    console.print(message)
    raise typer.Exit(code=code)


def _collect_results(
    query_text: str,
    domain: str | None,
    table_name: str,
    mode: str,
    top_k: int,
) -> list[tuple[str, SearchResult]]:
    """Collect search results across one or more vector tables.

    Parameters:
        query_text: Search query text.
        domain: Optional domain filter.
        table_name: Requested table name or `all`.
        mode: Search mode, `hybrid` or `vector`.
        top_k: Maximum number of results to collect.

    Returns:
        list[tuple[str, SearchResult]]: Ranked results paired with table names.
    """
    shared_embedder = Embedder()
    table_names = ["documents", "personal"] if table_name == "all" else [table_name]
    results: list[tuple[str, SearchResult]] = []

    for current_table in table_names:
        store = VectorStore(current_table, embedder=shared_embedder)
        if mode == "hybrid":
            table_results = store.hybrid_search(query_text, top_k=top_k)
        else:
            table_results = store.search(query_text, top_k=top_k, domain_filter=domain)

        if domain and mode == "hybrid":
            table_results = [item for item in table_results if item.domain == domain]

        results.extend((current_table, item) for item in table_results)

    results.sort(key=lambda pair: pair[1].score, reverse=True)
    return results[:top_k]


def _render_search_results(query_text: str, results: list[tuple[str, SearchResult]]) -> None:
    """Render ranked search results in a readable terminal table.

    Parameters:
        query_text: Original search query.
        results: Ranked results paired with source table names.
    """
    if not results:
        console.print("No results found.")
        return

    unique_tables = {table_name for table_name, _ in results}
    unique_sources = list(dict.fromkeys(result.source_file for _, result in results))
    console.print(f'Query: "{query_text}"')
    if len(unique_tables) == 1:
        console.print(f"Results from: {next(iter(unique_tables))} table")
    else:
        console.print("Results from: multiple tables")
    console.print(f"Sources: {', '.join(unique_sources)}")

    table = Table(title=f"Search Results: {query_text}")
    table.add_column("#")
    table.add_column("Table")
    table.add_column("Domain")
    table.add_column("Page")
    table.add_column("Section")
    table.add_column("Score")
    table.add_column("Source")
    table.add_column("Preview")

    for index, (current_table, result) in enumerate(results, start=1):
        preview = result.display_text.replace("\n", " ")
        if len(preview) > 110:
            preview = f"{preview[:107]}..."
        table.add_row(
            str(index),
            current_table,
            result.domain,
            str(result.page_number),
            result.section,
            f"{result.score:.4f}",
            result.source_file,
            preview,
        )

    console.print(table)


@app.command()
def health() -> None:
    """Show health status for the core local dependencies."""
    table = Table(title="Personal AI Brain Health")
    table.add_column("Dependency")
    table.add_column("Status")
    table.add_column("Detail")

    for status in collect_core_health():
        table.add_row(status.name, "ok" if status.ok else "failed", status.detail)

    console.print(table)


@app.command()
def route(
    domain: str = typer.Argument(..., help="Domain to evaluate."),
    requested_route: str = typer.Option("auto", "--requested-route", help="auto, local, or cloud."),
) -> None:
    """Show the resolved privacy route for a domain."""
    decision = choose_model_route(domain=domain, requested_route=requested_route)
    table = Table(title="Privacy Route Decision")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("domain", decision.domain)
    table.add_row("route", decision.route)
    table.add_row("allow_cloud", str(decision.allow_cloud))
    table.add_row("reason", decision.reason)
    console.print(table)


@app.command()
def search(
    query_text: str = typer.Argument(..., help="Query text to search for."),
    domain: str | None = typer.Option(None, "--domain", help="Optional domain filter."),
    table_name: str = typer.Option("all", "--table", help="documents, personal, or all."),
    mode: str = typer.Option("hybrid", "--mode", help="hybrid or vector."),
    top_k: int = typer.Option(5, "--top-k", "--top", help="Maximum number of results."),
) -> None:
    """Search the vector store and print ranked retrieval results."""
    if table_name not in {"documents", "personal", "all"}:
        _fail_cli("table must be one of: documents, personal, all")
    if mode not in {"hybrid", "vector"}:
        _fail_cli("mode must be one of: hybrid, vector")
    if top_k < 1:
        _fail_cli("top-k must be >= 1")
    results = _collect_results(query_text, domain, table_name, mode, top_k)
    _render_search_results(query_text, results)


@app.command()
def count(
    table_name: str = typer.Option("all", "--table", help="documents, personal, or all."),
) -> None:
    """Show stored row counts for one or more vector tables."""
    if table_name not in {"documents", "personal", "all"}:
        _fail_cli("table must be one of: documents, personal, all")

    table_names = ["documents", "personal"] if table_name == "all" else [table_name]
    table = Table(title="Vector Store Counts")
    table.add_column("Table")
    table.add_column("Count")

    total = 0
    for current_table in table_names:
        store = VectorStore(current_table)
        row_count = store.count()
        total += row_count
        table.add_row(current_table, str(row_count))

    if table_name == "all":
        table.add_row("total", str(total))

    console.print(table)


def main() -> None:
    known_commands = {"health", "route", "search", "count"}
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith("-"):
        legacy_args = sys.argv[1:]
        query_text = legacy_args[0]
        domain: str | None = None
        top_k = 5
        mode = "hybrid"
        table_name = "all"

        index = 1
        while index < len(legacy_args):
            arg = legacy_args[index]
            if arg == "--domain" and index + 1 < len(legacy_args):
                domain = legacy_args[index + 1]
                index += 2
                continue
            if arg in {"--top", "--top-k"} and index + 1 < len(legacy_args):
                top_k = int(legacy_args[index + 1])
                index += 2
                continue
            if arg == "--mode" and index + 1 < len(legacy_args):
                mode = legacy_args[index + 1]
                index += 2
                continue
            if arg == "--table" and index + 1 < len(legacy_args):
                table_name = legacy_args[index + 1]
                index += 2
                continue
            index += 1

        search(query_text=query_text, domain=domain, table_name=table_name, mode=mode, top_k=top_k)
    else:
        app()


if __name__ == "__main__":
    main()
