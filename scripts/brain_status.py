# MODULE: Health check for all brain services.
"""Brain Status dashboard to verify service health."""

import httpx
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

def check_service(name: str, url: str) -> bool:
    try:
        resp = httpx.get(url, timeout=2.0)
        return resp.status_code == 200
    except Exception:
        return False

def main():
    console = Console()
    table = Table(title="🧠 Personal AI Brain — Service Status")
    table.add_column("Service", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Endpoint", style="dim")

    # 1. Ollama
    ollama_ok = check_service("Ollama", "http://localhost:11434/api/tags")
    table.add_row("Ollama (LLM)", "[green]ONLINE[/]" if ollama_ok else "[red]OFFLINE[/]", "http://localhost:11434")

    # 2. Letta
    letta_ok = check_service("Letta", "http://localhost:8283/v1/health/")
    table.add_row("Letta (Memory)", "[green]ONLINE[/]" if letta_ok else "[red]OFFLINE[/]", "http://localhost:8283")

    # 3. FastAPI (if running)
    fastapi_ok = check_service("API", "http://localhost:8001/health")
    table.add_row("FastAPI (Core)", "[green]ONLINE[/]" if fastapi_ok else "[red]OFFLINE[/]", "http://localhost:8001")

    # 4. LanceDB (file check)
    db_path = Path("data/vectordb")
    db_ok = db_path.exists()
    table.add_row("LanceDB (Store)", "[green]ONLINE[/]" if db_ok else "[red]MISSING[/]", str(db_path))

    console.print(table)

    if not all([ollama_ok, letta_ok, db_ok]):
        console.print("\n[yellow]⚠ Warning: Some core services are offline. Run 'docker-compose up -d' first.[/]")
        sys.exit(1)
    else:
        console.print("\n[green]✓ All systems operational.[/]")

if __name__ == "__main__":
    main()
