# MODULE: Interactive terminal script for the 9 PM nightly review and reflection.
"""Interactive CLI for collecting and saving a nightly daily-review log."""

import datetime

import typer
from rich.console import Console
from rich.prompt import Prompt

from config import LOGS_DIR

app = typer.Typer(help="Complete your daily reflection for the AI Brain.")
console = Console()


@app.command()
def main() -> None:
    """Prompt the user with 5 questions and save the answers to a Markdown log."""
    console.print("[bold blue]Daily Review[/bold blue]", justify="center")
    console.print("Answer the following 5 questions to complete your daily review.\n")

    questions = {
        "Focus": "What was your main focus today?",
        "Learning": "What did you learn today?",
        "Mistakes": "What mistakes did you make and what did you learn from them?",
        "Tomorrow": "What is your top priority for tomorrow?",
        "Message": "A message to your future self?"
    }

    answers = {}
    for key, question in questions.items():
        answers[key] = Prompt.ask(f"[bold green]{key}[/bold green]: {question}")

    # Prepare markdown content
    date_str = datetime.date.today().isoformat()
    content = f"# Daily Review - {date_str}\n\n"
    for key, answer in answers.items():
        content += f"## {key}\n{answer}\n\n"

    # Save to data/logs/
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = LOGS_DIR / f"{date_str}.md"

    with file_path.open("w", encoding="utf-8") as handle:
        handle.write(content)

    console.print(f"\n[bold green]Success![/bold green] Review saved to {file_path}")


if __name__ == "__main__":
    app()
